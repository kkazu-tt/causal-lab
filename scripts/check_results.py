"""各ページが _results/<key>.json に書いた推定値を確かめる（R/setup.R の record()）。

次のどれかで失敗する。
- methods/ のページなのに結果が無い（ページが最後まで実行されていない）
- 推定値が、ページに書いた想定の範囲（expect）の外にある（パッケージの更新で既定値や計算が変わった）
- R と Python で同じ推定をした値（<名前> と <名前>_python）が一致しない
"""

import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent
problems = []

for qmd in sorted((root / "methods").glob("*.qmd")):
    key = qmd.stem
    path = root / "_results" / f"{key}.json"
    if not path.exists():
        problems.append(f"{key}: 結果がありません（ページが最後まで実行されていない）")
        continue
    r = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ("method", "page", "estimate", "se", "expect") if k not in r]
    if missing:
        problems.append(f"{key}: 結果に {', '.join(missing)} がありません")
        continue
    lo, hi = r["expect"]
    ok = lo <= r["estimate"] <= hi
    print(f"{key}: {r['estimate']:.4f}（想定 [{lo}, {hi}]）{'' if ok else ' ← 範囲外'}")
    if not ok:
        problems.append(f"{key}: 推定値 {r['estimate']:.4f} が想定の範囲 [{lo}, {hi}] の外です")
    for name, py in r.items():
        if name.endswith("_python"):
            base = name.removesuffix("_python")
            rv = r.get(base)
            if rv is None or abs(rv - py) > 1e-6 * max(1.0, abs(rv)):
                problems.append(f"{key}: {base} が R（{rv}）と Python（{py}）で一致しません")

if problems:
    print("\n".join(["", "検査に通りませんでした:"] + problems))
    sys.exit(1)
print("すべての推定値が想定の範囲に入り、R と Python の値も一致しました。")
