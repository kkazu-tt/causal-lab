# AGENTS.md

## このリポジトリ

因果推論・計量政治・計量経済の手法を、R と Python の実例で確かめる公開サイト（Quarto のウェブサイト）。
公開先は Cloudflare Workers の静的ファイルだけの Worker（https://causal-lab.kkazu.workers.dev 、設定は `wrangler.jsonc`）。
コードは GitHub（公開）に置く。利用の集計は Cloudflare Web Analytics（Cookie を使わない）。

最初に読むもの: この文書 → `README.md` → 手本のページ `methods/did.qmd`。

## 構成

| 場所 | 中身 |
|---|---|
| `methods/<key>.qmd` | 手法ごとのページ。`<key>` は結果のファイル名にも使う |
| `index.qmd` | ダッシュボード。各ページが書いた `_results/*.json` を読んで一覧にする（最後に描画する） |
| `environment.qmd` | 実行環境。R・Python・パッケージ・Quarto・ブラウザの中のエンジンの版を記録する |
| `R/setup.R` | 各ページが最初に読む。図の見た目と `record()` |
| `scripts/check_results.py` | 推定値が想定の範囲に入るか、R と Python が一致するかを確かめる |
| `scripts/check_live.py` | ヘッドレスの Chrome で各ページの「Run Code」を全部押し、ブラウザの中の例が動くかを確かめる |
| `scripts/serve.py` | `_site` を手元で配る（標準の http.server は同時の読み込みで接続がリセットされる） |
| `_extensions/r-wasm/live` | quarto-live（ブラウザの中の R と Python）。CI は毎回最新のリリースで置き換える |
| `DESCRIPTION` / `pyproject.toml` | CI が入れる R と Python のパッケージの一覧（版は固定しない） |
| `wrangler.jsonc` / `package.json` | Cloudflare への配備。wrangler だけは版を固定し、Dependabot が上げる |

## ページの規約

- front matter は `format: live-html` と `engine: knitr`。本文の最初に `{{< include ../_extensions/r-wasm/live/_knitr.qmd >}}` を置き、隠したチャンクで `source("R/setup.R")` する。コードはプロジェクトの根で動く（`execute-dir: project`）
- 節の順: 何を推定するか → 識別の仮定 → 実データの例（R と Python のタブ）→ ブラウザで試す → 落とし穴 → 参考文献
- 実データは R のパッケージに付いたものを R で読み、Python へは reticulate で渡す（`r.<名前>`）。CSV を作って配らない（データの再配布を避けるため）
- R と Python で同じ推定をしたら、`record()` に `<名前>` と `<名前>_python` を両方書く。CI が一致を確かめる
- `record("<key>", method, page, data, question, estimand, estimate, se, estimator, expect = c(下限, 上限))` を必ず呼ぶ。推定量に固有の区間があるなら `ci = c(下限, 上限)` と `ci_label` も書く（ダッシュボードは ±1.96×se の代わりにそれを出す）。`expect` は公表値か、いまの推定値の近くの狭い範囲。パッケージの更新で既定値や計算が変わったら CI が止まる
- ブラウザで試す例は、作ったデータ（シミュレーション）と、基本の R か numpy・pandas・statsmodels で書く（読者の読み込みを軽くするため）。Python のパッケージは import すると自動で読み込まれるので、front matter に `pyodide:` を書かない。webR でパッケージが要るときだけ `webr: packages: [...]` を書く
- 入力のスライダーは OJS（`viewof x = Inputs.range(...)`、`//| echo: false`）で作り、webR のブロックに `#| input:` と `#| autorun: true` を付ける
- 文章は常体（だ・である）。1文に1つのことを書き、主張には参考文献を付ける。図は `R/setup.R` の色（`col_main`・`col_second`）を使い、凡例は2系列以上のときだけ付ける

## 版の方針

R・R のパッケージ・Python・Python のパッケージ・Quarto・quarto-live は版を固定しない。CI が毎回最新を入れて作り直し、
描画 → `check_results.py` → `check_live.py` の全部が通ったときだけ公開する。落ちたら公開は前の版のままで、
`report-failure.yml` が Issue を立てる。使った版は `environment.qmd` のページに残る。

ブラウザの中の webR と Pyodide の版は、quarto-live の既定に任せる。2026-10-21 に Pyodide だけを最新（314.0.7）にすると、
読み込むファイルの名前が変わっていて quarto-live 0.2.0 では動かなかった。版の組み合わせは quarto-live の作者が確かめたものを使う。

## 手元での確認

```sh
export PATH="$HOME/.local/quarto/1.10.19/bin:$PATH"   # Quarto は ~/.local/quarto に展開してある
uv sync                                                # Python の依存（.venv）
quarto render                                          # 全ページ。1ページなら quarto render methods/did.qmd
python3 scripts/check_results.py
python3 scripts/serve.py 8765 &                        # サンドボックスの外で
uv run --no-project --with playwright python scripts/check_live.py http://127.0.0.1:8765   # サンドボックスの外で
```

## 環境の注意（Claude Code のサンドボックス）

- `.git` への書き込み（`git init`・`commit`）、`quarto add`（Deno が macOS の証明書を読めない）、ポートの待ち受け（`serve.py`）、Chrome の起動（`check_live.py`）、R のパッケージの導入は、サンドボックスの外で実行する
- R のパッケージは CRAN のバイナリで入れる（`install.packages(..., type = "binary")`）。cregg は R 4.6 のバイナリが無い（2026-10-21）

## 公開と並行作業

- 公開は CI（`.github/workflows/build-deploy.yml`）だけが行う。配備のジョブは描画のジョブと分け、Cloudflare の合鍵（secret の `CLOUDFLARE_API_TOKEN`・`CLOUDFLARE_ACCOUNT_ID`）はそこにだけ渡す。本番の確認に落ちたら配備の前の版に戻す
- 手元からの配備（`npx wrangler deploy`、サンドボックスの外）は、CI が使えないときの非常手段に限る
- main への直接の push で運用する。push の前に `quarto render` と2つの検査を手元で通す
- ステージは自分が触ったパスを名指しする。検証が済んだ作業はすぐにコミットする
- 持ち主の非公開ノートや授業資料を本文に写さない。本文と例は公開の文献とデータで書く
