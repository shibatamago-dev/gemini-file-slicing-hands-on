"""Create the fictional dummy workbook used in the slicing verification.

All values are made up. Structure:
- Sheet1 "在庫メモ": 150 rows of unrelated dummy inventory.
- Sheet2 "売上サマリー": the target table (A1:D10). Rows below the target
  range hold out-of-range values 9999 / 8888 so contamination is visible.
  Correct sums for B2:D10: 521 / 593 / 703, total 1817.
- Sheet3 "別店舗ダミー": a confuser table where every value is 777.

Usage: python3 make_dummy.py  (writes dummy_sales.xlsx next to this file)
Requires: openpyxl
"""
import os
import random

from openpyxl import Workbook

random.seed(42)
wb = Workbook()

ws1 = wb.active
ws1.title = "在庫メモ"
ws1.append(["商品コード", "商品名", "在庫数", "保管場所"])
names = ["ダミー文具", "ダミー食品", "ダミー雑貨", "ダミー部品", "ダミー書籍"]
for i in range(1, 151):
    ws1.append([f"D-{i:04d}", f"{names[i % len(names)]}{i}", random.randint(0, 500), f"棚{chr(65 + i % 8)}-{i % 20 + 1}"])

ws2 = wb.create_sheet("売上サマリー")
ws2.append(["商品名", "4月", "5月", "6月"])
items = [
    ("りんごジュース", 120, 135, 150),
    ("みかんゼリー", 80, 82, 79),
    ("ぶどうパン", 45, 60, 88),
    ("ももジャム", 30, 28, 35),
    ("なしタルト", 55, 70, 65),
    ("すももソーダ", 90, 95, 130),
    ("びわクッキー", 25, 40, 38),
    ("かき氷シロップ", 10, 22, 60),
    ("うめキャンディ", 66, 61, 58),
]
for row in items:
    ws2.append(list(row))
ws2.append(["番外・対象外A", 9999, 9999, 9999])
ws2.append(["番外・対象外B", 8888, 8888, 8888])

ws3 = wb.create_sheet("別店舗ダミー")
ws3.append(["商品名", "4月", "5月", "6月"])
for name, *_ in items:
    ws3.append([name, 777, 777, 777])

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_sales.xlsx")
wb.save(out)

b = [r[1] for r in items]
c = [r[2] for r in items]
d = [r[3] for r in items]
print(f"wrote {out}")
print("B sum", sum(b), "C sum", sum(c), "D sum", sum(d), "total B2:D10", sum(b + c + d))
