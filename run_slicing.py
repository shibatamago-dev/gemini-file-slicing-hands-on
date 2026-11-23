"""Call the Gemini Interactions API with a local document file.

The API key is read from the GEMINI_API_KEY environment variable and sent
as the x-goog-api-key header. Get a key at https://aistudio.google.com/apikey
(the free tier is enough; note that failed requests also count against the
free-tier daily quota).

Spec format (JSON):
  {
    "model": "gemini-4-hydrogen",
    "file": "dummy_sales.xlsx",
    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "prompt": "...",
    "document_extra": {
      "processing": {"type": "static",
                     "spreadsheet_options": {"sheet_index": 2,
                                             "visible_cells": "B2:D10",
                                             "content_layers": ["data"]}}
    }
  }

"document_extra" is optional. Omit it to send the whole file, or add a
"processing" block to slice the file (page ranges for documents, sheet and
cell ranges for spreadsheets, time intervals for audio/video).

Prints the raw API response as JSON. A one-line summary (usage and elapsed
time on your machine) goes to stderr. Elapsed time includes network and
connection overhead; it is not a measure of model speed.

Usage:
  export GEMINI_API_KEY="your key"
  python3 run_slicing.py --spec spec_full.json
  python3 run_slicing.py --spec spec_sliced.json
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def main(argv):
    if len(argv) != 3 or argv[1] != "--spec":
        print("usage: run_slicing.py --spec /path/to/spec.json", file=sys.stderr)
        return 2
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set", file=sys.stderr)
        return 2
    with open(argv[2], encoding="utf-8") as f:
        spec = json.load(f)
    here = os.path.dirname(os.path.abspath(argv[2]))
    file_path = spec["file"]
    if not os.path.isabs(file_path):
        file_path = os.path.join(here, file_path)
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    doc_block = {
        "type": "document",
        "data": data,
        "mime_type": spec["mime_type"],
    }
    doc_block.update(spec.get("document_extra") or {})
    body = {
        "model": spec.get("model", "gemini-4-hydrogen"),
        "input": [
            doc_block,
            {"type": "text", "text": spec["prompt"]},
        ],
    }
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Api-Revision": "2026-05-20",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1
    elapsed = time.time() - started
    print(json.dumps(result, ensure_ascii=False, indent=2))
    usage = result.get("usage") or result.get("usage_metadata") or {}
    print(f"[summary] elapsed={elapsed:.1f}s usage={json.dumps(usage, ensure_ascii=False)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
