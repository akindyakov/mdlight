#!/usr/bin/env python2

import argparse
import logging
import os
import sys
import re

import BaseHTTPServer

import mako.template


_log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="Directory with markdown pages.",
    )
    parser.add_argument(
        "--style",
        metavar="CSS_FILE",
        help="CSS style for all pages.",
    )
    parser.add_argument(
        "--template",
        metavar="MAKO_FILE",
        help="Template for all pages with {{content}} block inside.",
    )
    parser.add_argument(
        "--cache-size",
        metavar="INT",
        default=17,
        type=int,
        help="Cache size in pages, default %(default)s.",
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


class PageNode(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def page(self):
        with open(self.filepath) as fin:
            return fin.read()


class MapNode(object):
    RE_TITLE = re.compile("\s*#([^#].*)")
    @staticmethod
    def _extract_title(pathname):
        title = os.path.basename(pathname)
        if not os.path.isdir(pathname):
            with open(pathname) as fin:
                for (num, line) in enumerate(fin):
                    if num > 10:
                        break
                    m = MapNode.RE_TITLE.match(line)
                    if m:
                        title += ": " + m.groups()[0].strip()
                        break
        return title

    class Item(object):
        def __init__(self, title, path):
            self.title = title
            self.path = path

    def __init__(self, path):
        self.path = path
        self.items = list()

    def add(self, filepath, relpath):
        _log.debug("Add %s to %s", filepath, relpath)
        self.items.append(
            self.Item(
                title=self._extract_title(filepath),
                path=relpath,
            )
        )

    def page(self):
        return "<ul>{}</ul>".format(
            "".join(
                """<li><a href="{path}">{title}</a></li>""".format(
                    path=item.path,
                    title=item.title,
                )
                for item in self.items
            )
        )


def skip_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def build_tree(root_path):
    tree = dict()
    for (dirpath, dirnames, filenames) in os.walk(root_path, followlinks=True):
        map_node = MapNode(dirpath)
        for filename in filenames:
            if filename.endswith(".md") or filename.endswith(".markdown"):
                filepath = os.path.join(dirpath, filename)
                relpath = skip_prefix(filepath, root_path)
                tree[relpath] = PageNode(filepath)
                map_node.add(filepath, relpath)
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            relpath = skip_prefix(path, root_path)
            map_node.add(path, relpath)
        relpath = skip_prefix(dirpath, root_path)
        tree[relpath] = map_node
    return tree


class Handler2(BaseHTTPServer.BaseHTTPRequestHandler):
    tree = None

    def _success(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _error(self, code=500):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        node = self.tree.get(
            self.path.strip("/")
        )
        if node:
            self._success()
            self.wfile.write(
                node.page()
            )
        else:
            self._error(404)

    def do_HEAD(self):
        self._success()

    def do_POST(self):
        self._error()
        self.wfile.write("Not implemented")


def run_server(tree, host, port):
    server_address = ('', port)
    Handler2.tree = tree
    httpd = BaseHTTPServer.HTTPServer(
        (host, port),
        Handler2,
    )
    _log.debug("Run server on %s:%d", host, port)
    httpd.serve_forever()


def main():
    args = parse_args()
    tree = build_tree(args.dir)
    run_server(tree, args.hostname, args.port)


if __name__ == "__main__":
    try:
        _log = logging.getLogger("main")
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
