import copy
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipeline import core as c

NOW = dt.datetime(2026, 10, 27, 2, tzinfo=c.UTC)


def paper(key='2610.99991', published='2026-10-26T09:00:00Z', title='Generative recommendation with semantic IDs'):
    return {'id':key,'title':title,'abstract':'We improve generative recommendation using prefix-balanced semantic identifiers. Experiments show promising retrieval accuracy.',
            'published':published,'updated':published,'version':1,'authors':['A. Researcher'],'categories':['cs.IR'],'window':'72h'}


def review():
    return {'relevant':True,'score':91,'topics':['Semantic ID'],'reading':'必读','summary':'基于摘要生成的测试摘要。','why_read':'适合验证语义标识的负载均衡。',
            'limitations':'只读取摘要，未验证全文和线上收益。','experiment':'对比 Prefix 级流量分布和 Recall@K。','evidence_quote':'We improve generative recommendation using prefix-balanced semantic identifiers.'}


class FakeClient:
    def __init__(self, result=None):
        self.result = result
        self.payload = None

    def request(self, url, payload=None, key=None):
        self.payload = payload
        return json.dumps(self.result or {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(review())}]}],
                                         'usage':{'input_tokens':1000,'output_tokens':400}}).encode()


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root/'data').mkdir()
        (self.root/'config.json').write_text((c.ROOT/'config.json').read_text())
        for name, data in [('history.jsonl',''),('days.json','{}'),('evaluations.json','{}'),('aliases.json','{}'),('exclusions.json','{}')]:
            (self.root/'data'/name).write_text(data)
        self.config = c.read_json(self.root/'config.json')

    def tearDown(self):
        self.tmp.cleanup()

    def snapshots(self):
        return {f.name:f.read_bytes() for f in (self.root/'data').iterdir()}

    def seed(self):
        row = c.normalize_record({**paper(),**review(),'recommended_on':'2026-10-26'})
        (self.root/'data/history.jsonl').write_text(c.history_text([row]))
        (self.root/'data/days.json').write_text(c.dump({'2026-10-26':{'status':'imported','ids':[row['id']]}}))

    def test_arxiv_version_and_url_normalization(self):
        for value in ['2610.23453v3','arXiv:2610.23453v1','https://arxiv.org/abs/2610.23453v2?x=1','https://arxiv.org/pdf/2610.23453v2.pdf','https://doi.org/10.48550/arXiv.2610.23453']:
            self.assertEqual(c.canonical_id(value),'2610.23453')
        self.assertEqual(c.canonical_id('https://arxiv.org/abs/cs/9901001v2'),'cs/9901001')
        with self.assertRaises(c.SafeError): c.canonical_id('javascript:alert(1)')

    def test_import_merge_preserves_records_and_earliest_date(self):
        self.seed()
        file = self.root/'import.jsonl'
        file.write_text(c.history_text([{**paper(),'id':'2610.99991v3','recommended_on':'2026-10-25','summary':'do not overwrite'},
                                      {**paper('2610.99992'),'recommended_on':'2026-10-24'}]))
        result = c.import_history(file,self.root)
        self.assertEqual(result['after'],2)
        rows=c.load_history(self.root/'data/history.jsonl')
        existing=next(r for r in rows if r['id']=='2610.99991')
        self.assertNotEqual(existing['summary'],'do not overwrite')
        self.assertEqual(existing['recommended_on'],'2026-10-25')
        c.validate_state(rows,c.read_json(self.root/'data/days.json'))
        self.assertEqual(c.import_history(file,self.root)['added'],0)

    def test_invalid_import_does_not_mutate(self):
        self.seed(); before=self.snapshots(); f=self.root/'broken.jsonl';f.write_text('{broken')
        with self.assertRaises(c.SafeError):c.import_history(f,self.root)
        self.assertEqual(before,self.snapshots())

    def test_missing_secret_does_not_mutate(self):
        self.seed();before=self.snapshots()
        with patch.dict(os.environ,{},clear=True),self.assertRaises(c.SafeError):c.update(self.root,NOW)
        self.assertEqual(before,self.snapshots())

    def test_partial_llm_failure_does_not_mutate(self):
        before=self.snapshots()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=([paper(),paper('2610.99992')],2)),patch.object(c,'evaluate',side_effect=[(review(),{}),c.SafeError('failure')]):
            with self.assertRaises(c.SafeError):c.update(self.root,NOW)
        self.assertEqual(before,self.snapshots())

    def test_fetch_failure_does_not_mutate(self):
        self.seed();before=self.snapshots()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',side_effect=c.SafeError('network')):
            with self.assertRaises(c.SafeError):c.update(self.root,NOW)
        self.assertEqual(before,self.snapshots())

    def test_success_and_idempotence(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=([paper()],1)),patch.object(c,'evaluate',return_value=(review(),{'input_tokens':100,'output_tokens':50})) as ev:
            result=c.update(self.root,NOW)
            self.assertEqual(result['picks'],1)
            self.assertEqual(c.update(self.root,NOW)['status'],'already_published')
            self.assertEqual(ev.call_count,1)
        self.assertEqual(len(c.load_history(self.root/'data/history.jsonl')),1)

    def test_empty_issue_is_distinct_from_error(self):
        self.seed()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=([],0)):
            result=c.update(self.root,NOW)
        self.assertEqual(result['status'],'empty')
        self.assertEqual(len(c.load_history(self.root/'data/history.jsonl')),1)
        self.assertEqual(c.read_json(self.root/'data/days.json')['2026-10-27']['ids'],[])

    def test_alias_and_exact_title_dedup(self):
        self.seed();(self.root/'data/aliases.json').write_text('{"2610.99992":"2610.99991"}')
        candidates=[paper(),paper('2610.99992',title='Different alias title'),paper('2610.99993')]
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=(candidates,3)),patch.object(c,'evaluate') as ev:
            self.assertEqual(c.update(self.root,NOW)['picks'],0)
            ev.assert_not_called()

    def test_budget_and_backfill_reservation(self):
        self.config['max_candidates']=3;self.config['max_calls_per_run']=3
        (self.root/'config.json').write_text(c.dump(self.config))
        papers=[paper(f'2610.{90000+i}',title=f'Recommendation {i}') for i in range(8)]
        older=paper('2610.88888',published='2026-10-21T12:00:00Z',title='Sequence compression')
        older['window']='7d_backfill';papers.append(older)
        seen=[]
        def ev(p,*args):seen.append(p['id']);return review(),{}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=(papers,9)),patch.object(c,'evaluate',side_effect=ev):c.update(self.root,NOW)
        self.assertEqual(len(seen),3);self.assertIn('2610.88888',seen)
        self.assertEqual(c.read_json(self.root/'data/days.json')['2026-10-27']['deferred'],6)

    def test_manual_exclusion_works_even_if_old_history_missing(self):
        (self.root/'data/exclusions.json').write_text('{"2610.99991":"known overlap"}')
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),patch.object(c,'harvest',return_value=([paper()],1)),patch.object(c,'evaluate') as ev:
            self.assertEqual(c.update(self.root,NOW)['picks'],0)
            ev.assert_not_called()

    def test_review_rejects_unbacked_evidence_and_bad_score(self):
        bad=review();bad['evidence_quote']='Claim never mentioned in source abstract'
        with self.assertRaises(c.SafeError):c.validate_review(bad,paper(),self.config)
        bad=review();bad['score']=True
        with self.assertRaises(c.SafeError):c.validate_review(bad,paper(),self.config)

    def test_responses_api_contract_and_no_store(self):
        client=FakeClient()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'},clear=True):r,usage=c.evaluate(paper(),self.config,client)
        self.assertEqual(r['score'],91);self.assertFalse(client.payload['store'])
        self.assertEqual(client.payload['text']['format']['type'],'json_schema')
        self.assertNotIn('fake',json.dumps(client.payload))
        for result in [{'status':'incomplete'}, {'status':'completed','output':[{'type':'message','content':[{'type':'refusal','refusal':'No'}]}]}]:
            with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}),self.assertRaises(c.SafeError):c.evaluate(paper(),self.config,FakeClient(result))

    def test_api_base_rejects_credentials_and_http(self):
        for base in ['http://example.com/v1','https://user:pass@example.com/v1','https://example.com/?token=x']:
            with patch.dict(os.environ,{'OPENAI_API_KEY':'fake','LLM_BASE_URL':base}),self.assertRaises(c.SafeError):c.evaluate(paper(),self.config,FakeClient())

    def test_pagination_and_windows(self):
        self.config.update({'page_size':1,'max_fetch':5})
        feeds=[]
        for p in [paper(),paper('2610.99992','2026-10-21T00:00:00Z')]:
            feeds.append(f'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"><opensearch:totalResults>2</opensearch:totalResults><entry><id>http://arxiv.org/abs/{p['id']}v2</id><title>{p['title']}</title><summary>{p['abstract']}</summary><published>{p['published']}</published><updated>{p['updated']}</updated></entry></feed>'''.encode())
        client=FakeClient()
        with patch.object(client,'request',side_effect=feeds):rows,total=c.harvest(self.config,NOW,client)
        self.assertEqual(total,2);self.assertEqual({r['window'] for r in rows},{'72h','7d_backfill'})
        self.assertEqual(rows[0]['version'],2)
        self.config['max_fetch']=1
        with patch.object(client,'request',return_value=feeds[0]),self.assertRaises(c.SafeError):c.harvest(self.config,NOW,client)

    def test_invalid_feed_fails_closed(self):
        for body in [b'<html>rate limited</html>',b'not XML',b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/api/errors</id></entry></feed>']:
            with self.assertRaises(c.SafeError):c.parse_feed(body)

    def test_real_archive_build_is_publishable_and_secret_free(self):
        out=self.root/'public';result=c.build(c.ROOT,out)
        self.assertGreaterEqual(result['papers'],17)
        self.assertTrue((out/'index.html').exists())
        self.assertEqual(set(p.name for p in out.iterdir()),{'index.html','style.css','app.js','favicon.svg','data.json','history.jsonl','import-example.jsonl','.nojekyll'})
        code=(out/'app.js').read_text()
        self.assertNotIn('innerHTML',code)
        self.assertNotIn('OPENAI_API_KEY',(out/'data.json').read_text())


if __name__=='__main__':unittest.main()
