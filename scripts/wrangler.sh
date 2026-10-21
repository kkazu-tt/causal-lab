#!/usr/bin/env bash
# wrangler を動かし、標準出力と標準エラーのメールアドレスを伏せる。終了コードは wrangler のものを返す。
# 公開のリポジトリでは Actions のログも、ログの末尾を貼る失敗の Issue も誰でも読める。wrangler は認証に失敗すると
# whoami を実行し、持ち主のメールとメール入りのアカウント名を出す（wrangler 4.151.1 の cli.js で確認、2026-10-22）。
set -o pipefail
redact() { sed -E 's/[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}/[メールを伏せた]/g'; }
npx wrangler "$@" 2> >(redact >&2) | redact
