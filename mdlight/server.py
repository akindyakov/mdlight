#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a simplest markdown document viewer.

It scan {--dir} directory for markdown documents and run http server on it.
If not $MDLIGHT_DIR specified - current directory chosed by default.
To see documents just open any web-browser and got to
"http://{--host}:{--port}" website.
"""

from http import HTTPStatus
import argparse
import http.server
import logging
import os
import re
import sys


sys.path.append(
    os.path.dirname(
            os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


import mdlight.index.tree
from mdlight.index.pages import MarkdownPage, GraphvizPage


_REQUIRED_BINARIES = [
    MarkdownPage.BINARY_NAME,
    GraphvizPage.BINARY_NAME,
]


def __check_binary(binary):
    for path in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(path, binary)
        if os.path.exists(full_path):
            return True
    return False


_log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        default=os.path.expanduser(os.environ.get("MDLIGHT_DIR", os.curdir)),
        help="Directory with markdown pages, default: %(default)s.",
    )
    parser.add_argument(
        "--hostname",
        metavar="FILE",
        default="localhost",
        help="Hostname for the server, default: %(default)s.",
    )
    parser.add_argument(
        "--port",
        metavar="FILE",
        default=1600,
        type=int,
        help="Port for the server, default: %(default)s.",
    )
    return parser.parse_args()


class QueryHandler(http.server.BaseHTTPRequestHandler):
    tree = None

    def do_GET(self):
        node = self.tree.get(
            self.path.strip("/")
        )
        if node is None:
            self.send_response(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", node.content_type())
        self.send_header("Content-encoding", node.content_encoding())
        self.end_headers()
        self.wfile.write(
            node.content()
        )


def run_server(tree, host, port):
    server_address = (host, port)
    QueryHandler.tree = tree
    httpd = http.server.HTTPServer(
        server_address,
        QueryHandler,
    )
    _log.info("Run server on http://%s:%d", host, port)
    httpd.serve_forever()


def main():
    args = parse_args()
    tree = mdlight.index.tree.build_tree(args.dir)
    run_server(tree, args.hostname, args.port)


if __name__ == "__main__":
    try:
        for binary in _REQUIRED_BINARIES:
            if not __check_binary(binary):
                raise Exception(
                    "%s is not installed, or not in a PATH env" %
                    binary
                )

        _log = logging.getLogger(__name__)
        _log.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(
            logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        )
        _log.addHandler(ch)
        main()

    except SystemExit:
        raise

    except:
        _log.exception("Catched exception ")
        sys.exit(1)
