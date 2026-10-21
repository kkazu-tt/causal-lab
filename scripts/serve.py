"""_site を http://127.0.0.1:<port>/ で配る（手元の確認と、CI の配備前の検査に使う）。

標準の `python -m http.server` は待ち行列が5件で、ページが CSS と JS をまとめて読むと接続がリセットされるので広げる。
"""

import functools
import http.server
import sys


class Server(http.server.ThreadingHTTPServer):
    request_queue_size = 128


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 1ページで数十件の要求が出て、検査のログが読めなくなるため


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
handler = functools.partial(QuietHandler, directory="_site")
Server(("127.0.0.1", port), handler).serve_forever()
