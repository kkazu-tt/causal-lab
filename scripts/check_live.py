"""作ったサイトをヘッドレスの Chrome で開き、ブラウザの中の R（webR）と Python（Pyodide）の例が全部動くかを確かめる。

各ページの「Run Code」を上から順に押し、結果が出るまで待つ。結果が出ない、エラーが出る、ページの JavaScript が
落ちる、のどれかで失敗する（わざと失敗するページで、R と Python のエラーを両方とも捕まえることを確かめた）。curl の 200 では、ブラウザの中の R や Python が壊れていても気づけないため。

使い方（手元の _site は scripts/serve.py で配ってから。本番なら公開先の URL を渡す）:
  uv run --no-project --with playwright python scripts/check_live.py http://127.0.0.1:8765
Chrome は GitHub の ubuntu-24.04 のランナーと手元の Mac に入っているものを使う（channel="chrome"）。
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip("/")
# ページの一覧はリポジトリの methods/*.qmd から作る（本番を確かめるときは手元に _site が無いため）
root = pathlib.Path(__file__).resolve().parent.parent
pages = ["index.html", "environment.html"] + sorted(f"methods/{p.stem}.html" for p in (root / "methods").glob("*.qmd"))
problems = []

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    for path in pages:
        page = browser.new_page()
        # 検査で開いたページを利用の集計（Cloudflare Web Analytics）に数えさせない
        page.route("**/static.cloudflareinsights.com/**", lambda route: route.abort())
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        response = page.goto(f"{base}/{path}", wait_until="load")
        if response is None or response.status != 200:
            problems.append(f"{path}: ページを開けません（{response.status if response else '応答なし'}）")
            page.close()
            continue
        cells = page.locator(".exercise-cell")
        for i in range(cells.count()):
            cell = cells.nth(i)
            # 実行中は印（spinner）が出る。消えて、出力欄に何か入るまで待つ。初回はエンジンとパッケージの取得で遅い。
            # エンジンの取得の瞬断で落ちることがあるので（2026-10-21 に1回）、1回だけやり直す。
            error = None
            for attempt in range(2):
                try:
                    cell.locator(".exercise-editor-btn-run-code").click()
                    page.wait_for_function(
                        """c => c.querySelector('.exercise-editor-eval-indicator').classList.contains('d-none')
                             && c.querySelector('.cell-output-container').innerText.trim().length
                                + c.querySelectorAll('.cell-output-container img, .cell-output-container canvas').length > 0""",
                        arg=cell.element_handle(),
                        timeout=180_000,
                    )
                    error = None
                    break
                except Exception as e:
                    error = f"{type(e).__name__}: {str(e).splitlines()[0][:200]}"
                    print(f"::notice::{path} の {i + 1} 番目の例の {attempt + 1} 回目が失敗: {error}")
            if error:
                problems.append(f"{path} の {i + 1} 番目の例: 結果が出ません（{error}）")
                continue
            # R のエラーは「R Error」の枠（callout-important）に、Python のエラーはメッセージだけが stderr に出る。
            # 警告も stderr に出るので、Warning を含むものは知らせるだけにする。
            failed = cell.locator(".callout-important").all_inner_texts()
            for text in cell.locator(".cell-output-stderr").all_inner_texts():
                if "Warning" in text:
                    print(f"::notice::{path} の {i + 1} 番目の例の警告: {text.strip()[:200]}")
                else:
                    failed.append(text)
            if failed:
                problems.append(f"{path} の {i + 1} 番目の例: {' '.join(failed).strip()[:300]}")
        if errors:
            problems.append(f"{path}: ページの JavaScript が落ちました: {errors[0][:300]}")
        print(f"{path}: 例 {cells.count()} 個を実行")
        page.close()
    browser.close()

if problems:
    print("\n".join(["", "検査に通りませんでした:"] + problems))
    sys.exit(1)
print("すべてのページで、ブラウザの中の例が動きました。")
