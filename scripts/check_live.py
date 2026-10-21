"""作ったサイトをヘッドレスの Chrome で開き、ブラウザの中の R（webR）と Python（Pyodide）の例が全部動くかを確かめる。

各ページの「Run Code」を上から順に押し、結果が出るまで待つ。結果が出ない、エラーが出る、ページの JavaScript が
落ちる、のどれかで失敗する（わざと失敗するページで、R と Python のエラーを両方とも捕まえることを確かめた）。curl の 200 では、ブラウザの中の R や Python が壊れていても気づけないため。

使い方（_site を scripts/serve.py で配ってから）:
  uv run --with playwright python scripts/check_live.py http://127.0.0.1:8765
Chrome は GitHub の ubuntu-24.04 のランナーと手元の Mac に入っているものを使う（channel="chrome"）。
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip("/")
site = pathlib.Path(__file__).resolve().parent.parent / "_site"
pages = ["index.html"] + sorted(f"methods/{p.name}" for p in (site / "methods").glob("*.html"))
problems = []

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    for path in pages:
        page = browser.new_page()
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
            cell.locator(".exercise-editor-btn-run-code").click()
            # 実行中は印（spinner）が出る。消えて、出力欄に何か入るまで待つ。初回はエンジンとパッケージの取得で遅い。
            try:
                page.wait_for_function(
                    """c => c.querySelector('.exercise-editor-eval-indicator').classList.contains('d-none')
                         && c.querySelector('.cell-output-container').innerText.trim().length
                            + c.querySelectorAll('.cell-output-container img, .cell-output-container canvas').length > 0""",
                    arg=cell.element_handle(),
                    timeout=180_000,
                )
            except Exception:
                problems.append(f"{path} の {i + 1} 番目の例: 3分待っても結果が出ません")
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
