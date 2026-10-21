# 因果推論ラボ

因果推論・計量政治・計量経済の手法を、R と Python の実例で確かめるダッシュボード。
https://causal-lab.kkazu.workers.dev

## エージェント向けの入口

- 規則と構成: [AGENTS.md](AGENTS.md)
- ページの手本: [methods/did.qmd](methods/did.qmd)

| やりたいこと | コマンド |
|---|---|
| 全ページを作る | `quarto render` |
| 1ページだけ作る | `quarto render methods/did.qmd` |
| 推定値を確かめる | `python3 scripts/check_results.py` |
| ブラウザの中の例を確かめる | `python3 scripts/serve.py 8765 &` のあと `uv run --no-project --with playwright python scripts/check_live.py http://127.0.0.1:8765` |

変えてはいけない前提:

- 版は固定しない。CI が毎週と push のたびに最新の R・Python・パッケージで作り直し、検査が全部通ったときだけ公開する
- データは R のパッケージに付いたものを読む。CSV を作って配らない
- 非公開のノートや授業資料を本文に写さない

## ライセンス

- コード（R・Python・スクリプト、ページの中のコード片を含む）は MIT（[LICENSE](LICENSE)）
- ページの文章と図は [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)
- データは各 R パッケージのライセンスに、`_extensions/` の quarto-live はその作者のライセンスに従う

## 自動で回るもの

| いつ | 何を |
|---|---|
| main への push、毎週月曜 | 最新の R・Python・パッケージ・Quarto・quarto-live で作り直し、推定値とブラウザの中の例を確かめ、通れば Cloudflare Workers に公開して本番でも確かめる |
| 失敗したとき | 公開は前の版のまま（本番の確認に落ちたら前の版に戻す）。Issue が立つ |
