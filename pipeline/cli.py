import argparse
import json
import sys
from .core import ROOT, SafeError, build, import_history, load_history, prepare_review, publish_reviews, read_json, update, validate_state


def main():
    parser = argparse.ArgumentParser(description="Recommendation Paper Reading")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("update", help="Fetch + review + publish a new local daily issue (requires key)")
    sub.add_parser("build", help="Build static dist without network or secrets")
    sub.add_parser("validate", help="Validate IDs and day/history consistency")
    prep = sub.add_parser("prepare-review", help="Fetch candidates for Codex; no API key required")
    prep.add_argument("output")
    prep.add_argument("--preview", action="store_true", help="Inspect candidates even if today's issue already exists")
    publish = sub.add_parser("publish-reviews", help="Validate complete Codex reviews and update local ledger")
    publish.add_argument("snapshot")
    publish.add_argument("reviews")
    imp = sub.add_parser("import-history", help="Merge JSONL, never erase existing records")
    imp.add_argument("path")
    args = parser.parse_args()
    try:
        if args.command == "update":
            result = update()
        elif args.command == "build":
            result = build()
        elif args.command == "prepare-review":
            result = prepare_review(args.output, preview=args.preview)
        elif args.command == "publish-reviews":
            result = publish_reviews(args.snapshot, args.reviews)
        elif args.command == "import-history":
            result = import_history(args.path)
        else:
            rows = load_history(ROOT / "data/history.jsonl")
            validate_state(rows, read_json(ROOT / "data/days.json"))
            result = {"status": "valid", "papers": len(rows)}
        print(json.dumps(result, ensure_ascii=False))
    except SafeError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        # Never print raw HTTP errors, payloads, environment variables, or traceback.
        print("ERROR: " + type(exc).__name__ + "; aborted, review configuration or data", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
