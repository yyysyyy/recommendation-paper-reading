'use strict';
const $ = id => document.getElementById(id);
const state = {view:'daily', topic:'', search:'', reading:'', date:'', data:null, saved:new Set()};
function getLocal(key, fallback) {try {return localStorage.getItem(key) ?? fallback;} catch {return fallback;}}
function setLocal(key, value) {try {localStorage.setItem(key,value);} catch { /* Reading works without storage. */ }}
try {const ids=JSON.parse(getLocal('rpr-saved','[]')); if(Array.isArray(ids)) state.saved=new Set(ids.filter(x=>typeof x==='string'));} catch { /* Ignore corrupt browser-local bookmarks. */ }
if(getLocal('rpr-theme','light')==='dark') document.body.classList.add('dark');
function el(tag, cls, text) {const n=document.createElement(tag); if(cls)n.className=cls; if(text!==undefined)n.textContent=text; return n;}
function append(parent, ...children) {parent.append(...children);return parent;}
function link(text, href, cls='') {const a=el('a',cls,text);a.href=href;a.target='_blank';a.rel='noopener noreferrer';return a;}
function paperUrl(p,pdf=false) {return `https://arxiv.org/${pdf?'pdf':'abs'}/${encodeURI(p.id)}`;}
function publishedDate(p) {return p.published ? p.published.slice(0,10) : '日期待核验';}
function card(p,index) {
  const article=el('article','paper-card');
  article.dataset.paperId=p.id;
  append(article,append(el('div','score',p.score===null?'—':String(p.score)),el('small','','EDITOR SCORE')));
  const body=el('div','card-body');
  const top=el('div','card-top');
  append(top,el('span',`badge ${p.reading==='必读'?'must':''}`,p.reading==='必读'?'✳ 必读':p.reading));
  for(const t of p.topics.slice(0,3)) append(top,el('span','',t));
  const date=el('time','',`${publishedDate(p)} · ${p.window==='7d_backfill'?'7 天补漏':p.source==='conversation_recovery'?'历史恢复':'论文首发'}`);
  if(p.published)date.dateTime=p.published;append(top,date);
  append(body,top,append(el('h3'),link(p.title,paperUrl(p))),el('p','summary',p.summary));
  const shortWhy=p.why_read.split('\n\n').slice(0,2).join('\n\n').slice(0,280);
  if(p.why_read) append(body,append(el('div','why'),el('strong','','为什么值得读'),el('span','',shortWhy)));
  const actions=el('div','card-actions');
  append(actions,link('阅读论文 ↗',paperUrl(p),'paper-link'),link('PDF ↗',paperUrl(p,true)));
  const save=el('button','save','');save.type='button';
  const paintSave=()=>{save.textContent=state.saved.has(p.id)?'◆ 已存书签':'◇ 稍后读';save.classList.toggle('saved',state.saved.has(p.id));save.setAttribute('aria-pressed',String(state.saved.has(p.id)));};
  paintSave();save.addEventListener('click',()=>{state.saved.has(p.id)?state.saved.delete(p.id):state.saved.add(p.id);setLocal('rpr-saved',JSON.stringify([...state.saved]));paintSave();});
  append(actions,save,el('span','evidence',p.source==='conversation_recovery'?'原对话恢复 · 摘要未重新核验':'摘要辅助阅读 · '+p.id));
  append(body,actions);
  const details=el('details','details');append(details,el('summary','','实验启发与证据边界'));
  for(const [label,value] of [['最小验证实验',p.experiment||'原记录未单独提供，可结合摘要设计实验。'],['适用局限',p.limitations||'历史摘要来自原对话，本次未重新验证论文实验结论。'],['完整推荐理由',shortWhy!==p.why_read?p.why_read:''],['证据来源',p.evidence],['摘要原文摘录',p.evidence_quote||''],['首次推荐',p.recommended_on]]) if(value) append(details,append(el('p'),el('b','',label),el('span','',value)));
  append(body,details);append(article,body);return article;
}
function filters() {
  $('filters').replaceChildren();
  for(const topic of ['',...state.data.topics]) {const b=el('button','filter'+(topic===state.topic?' active':''),topic||'全部方向');b.type='button';b.setAttribute('aria-pressed',String(topic===state.topic));b.addEventListener('click',()=>{state.topic=topic;filters();render();});append($('filters'),b);}
}
function render() {
  if(!state.data)return;
  const d=state.data, history=state.view==='history', about=state.view==='about';
  $('reader').hidden=about;$('about').hidden=!about;
  for(const view of ['daily','history','about']) {const b=$('nav-'+view);b.classList.toggle('active',state.view===view);b.setAttribute('aria-current',state.view===view?'page':'false');}
  $('section-title').replaceChildren(document.createTextNode(history?'历史档案 ':'每日精选 '),el('span','',history?'The archive':'Daily picks'));
  $('section-kicker').textContent=history?'A GROWING RESEARCH ARCHIVE':'THE DAILY SELECTION';
  document.querySelector('.date-control').hidden=history;
  const q=state.search.toLowerCase().trim();
  const base=d.papers.filter(p=>history||p.recommended_on===state.date);
  const rows=base.filter(p=>(!state.topic||p.topics.includes(state.topic))&&(!state.reading||p.reading===state.reading)&&(!q||[p.title,p.id,p.summary,p.why_read,...p.topics].join(' ').toLowerCase().includes(q)));
  $('result-count').textContent=`${history?'全部档案':state.date} · ${rows.length} 篇${q||state.topic||state.reading?'匹配论文':'精选论文'}`;
  $('cards').replaceChildren(...rows.map(card));$('empty').hidden=rows.length>0;
  const day=d.days[state.date];
  $('empty-text').textContent=!history&&day?.status==='empty'?'本期检索成功，但没有达到筛选标准的新论文。宁缺毋滥，明天再见。':'没有符合当前条件的论文，试试其他方向或日期。';
  $('day-note').textContent=history?'按首次推荐日期归档；同一 arXiv 的不同版本只收录一次。':day?.status==='imported'?'本期从原对话恢复，评分与摘要沿用历史记录；未重新核验。':day?`检索 ${day.scanned??0} 条 · 模型评估 ${day.evaluated??0} 篇 · ${day.deferred??0} 篇因预算延后。${day.note||''}`:'';
  const url=new URL(location.href);url.hash=about?'about':history?'history':`daily/${state.date}`;historyReplace(url);
}
function historyReplace(url){window.history.replaceState(null,'',url);}
function viewFromHash(){const hash=location.hash.slice(1);state.view=hash==='history'?'history':hash==='about'?'about':'daily';if(hash.startsWith('daily/')&&state.data?.days[hash.slice(6)])state.date=hash.slice(6);$('date').value=state.date;render();}
function showAbout() {state.view='about';render();$('about').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
$('theme').addEventListener('click',()=>{document.body.classList.toggle('dark');setLocal('rpr-theme',document.body.classList.contains('dark')?'dark':'light');});
$('nav-daily').addEventListener('click',()=>{state.view='daily';render();});
$('nav-history').addEventListener('click',()=>{state.view='history';render();});
$('nav-about').addEventListener('click',showAbout);$('source-details').addEventListener('click',showAbout);
$('date').addEventListener('change',e=>{state.date=e.target.value;render();});
$('search').addEventListener('input',e=>{state.search=e.target.value;render();});
$('reading').addEventListener('change',e=>{state.reading=e.target.value;render();});
$('clear-filters').addEventListener('click',()=>{state.topic='';state.search='';state.reading='';$('search').value='';$('reading').value='';filters();render();});
window.addEventListener('hashchange',()=>{if(state.data)viewFromHash();});
async function init(){
  try {
    const response=await fetch('./data.json',{cache:'no-cache'});if(!response.ok)throw new Error('data_unavailable');
    state.data=await response.json();const d=state.data;
    const dates=Object.keys(d.days).sort().reverse();state.date=dates[0]||'';
    $('date').replaceChildren(...dates.map(date=>{const option=el('option','',date);option.value=date;return option;}));
    $('stat-papers').textContent=String(d.papers.length).padStart(2,'0');$('stat-days').textContent=String(dates.length).padStart(2,'0');$('stat-topics').textContent=String(d.topics.length).padStart(2,'0');
    $('last-date').textContent=state.date||'暂无日报';
    const today=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
    $('freshness').textContent=state.date&&state.date<today?'尚无今日更新 · 可继续阅读历史':'历史与自动日报均可追溯';
    const latest=d.papers.find(p=>p.recommended_on===state.date);$('note-date').textContent=state.date.replaceAll('-',' / ');
    if(latest){$('note-title').textContent=latest.title.split(':')[0];$('note-copy').textContent=(latest.experiment||latest.why_read||latest.summary).replace(/^原日报当日实验建议：\s*/,'').split('\n\n').slice(0,2).join(' ').slice(0,125);}
    else{$('note-title').textContent='宁缺毋滥，明天再读。';$('note-copy').textContent='本期没有达到筛选标准的新论文。历史档案仍有值得回访的想法。';}
    const provenance=`已恢复 ${d.provenance.recovered_records} 篇原对话记录；原对话提到约 ${d.provenance.expected_records} 篇，最早 ${d.provenance.missing_records} 篇明细缺失。Library JSONL 未取得，无法保证完整历史去重。可由维护者导入补齐。`;
    $('provenance-text').textContent=provenance;$('source-notice').textContent=provenance;
    filters();viewFromHash();
  } catch {
    $('result-count').textContent='论文数据加载失败';$('empty').hidden=false;$('empty-text').textContent='请刷新重试。维护者请检查构建产物是否包含 data.json。';$('source-notice').textContent='数据暂不可用；未将此状态视为零篇日报。';
  }
}
init();
