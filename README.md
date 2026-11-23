# Gemini API file slicing — hands-on reproduction

Reproduction code for a hands-on verification of the Gemini API's multimodal
file processing and **slicing** feature (announced in the Gemini API changelog
on 2026-11-18): pass an Office/OpenDocument file to the API, but process only
the part you need — a page range, a worksheet tab, a cell range, a time
interval, selected content layers.

Companion article (Japanese, Zenn):
「Gemini APIのファイル「スライシング」を試した：Excelの必要範囲だけ渡したら入力トークンが約94%減った」
(under review / to be published)

## What was verified

Using a fictional 3-sheet Excel workbook and the same prompt in both
conditions ("sum each column of B2:D10 on the second sheet"):

| Condition | Input tokens | Answer |
|---|---|---|
| Whole file (no `processing`) | 5,437 | 521 / 593 / 703 / total 1,817 (correct) |
| Sliced (sheet 2, `B2:D10`, `data` layer only) | 312 | 521 / 593 / 703 / total 1,817 (correct) |

Input tokens dropped by about 94% (to roughly 1/17). A probe question about
an out-of-range sheet, asked with the slice still applied, was answered with
"cannot be read" — the model could not see outside the slice, and did not
guess. Full details, including failure notes (intermittent HTTP 503s that
night), are in [RESULTS.md](RESULTS.md).

The slicing is specified on the document block:

```json
"processing": {
  "type": "static",
  "spreadsheet_options": {
    "sheet_index": 2,
    "visible_cells": "B2:D10",
    "content_layers": ["data"]
  }
}
```

## Files

- `make_dummy.py` — generates the fictional workbook `dummy_sales.xlsx`
  (sheet 1: 150 rows of unrelated inventory; sheet 2: the target table with
  out-of-range trap values 9999/8888 below it; sheet 3: an all-777 confuser).
- `run_slicing.py` — sends a file + prompt to the Interactions API
  (`gemini-4-hydrogen`) and prints the raw response and token usage.
- `spec_full.json` / `spec_sliced.json` / `spec_probe.json` — the three runs.
- `RESULTS.md` — measured results and caveats (in Japanese).

## Run it yourself

```bash
pip install openpyxl
python3 make_dummy.py

export GEMINI_API_KEY="your key"   # free key: https://aistudio.google.com/apikey
python3 run_slicing.py --spec spec_full.json
python3 run_slicing.py --spec spec_sliced.json
python3 run_slicing.py --spec spec_probe.json
```

Notes:

- The free tier allows about 20 requests per day, and **failed requests also
  count**. The three specs above are all you need; don't loop them.
- The original verification ran the same REST payload from the author's agent
  environment, with the key supplied through that environment's registered
  connection. This public version reads the key from `GEMINI_API_KEY`; the
  request body is identical.
- Response times depend heavily on your network path. Do not read them as
  model speed.

## License

MIT — see [LICENSE](LICENSE). All data in the workbook is fictional.
