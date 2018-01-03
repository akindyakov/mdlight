#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a simplest markdown document viewer.

It scan {--dir} directory for markdown documents and run http server on it.
To see documents just open any web-browser and got to
"http://{--host}:{--port}" website.
"""

from http import HTTPStatus
import argparse
import http.server
import logging
import mimetypes
import os
import re
import subprocess
import sys


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


class INode(object):
    mime_type_ = "text/html"
    encoding_ = None
    title_ = None

    def content_type(self):
        return self.mime_type_

    def content_encoding(self):
        return self.encoding_

    def title(self):
        return self.title_


class MdNode(INode):
    RE_FIRST_HEADER = re.compile("\s*#([^#].*)")
    @staticmethod
    def _extract_title(pathname):
        title = os.path.basename(pathname)
        if not os.path.isdir(pathname):
            with open(pathname) as fin:
                for (num, line) in enumerate(fin):
                    if num > 10:
                        break
                    m = MdNode.RE_FIRST_HEADER.match(line)
                    if m:
                        title += ": " + m.groups()[0].strip()
                        break
        return title

    ACCEPTED_EXTENSIONS = {".markdown", ".md", ".tex"}

    def __init__(self, filepath):
        _log.debug("Markdown node %r", filepath)
        self.filepath = filepath
        self.title_ = self._extract_title(filepath)
        self.encoding_ = "utf-8"

    def page(self):
        proc = subprocess.Popen(
            ["pandoc", self.filepath, "--to", "html5"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        text = proc.stdout.read()
        proc.wait()
        return text


class MapNode(INode):
    class Item(object):
        def __init__(self, title, path):
            self.title = title
            self.path = path

    def __init__(self, path):
        _log.debug("Map node %r", path)
        self.path = path
        self.items = list()

    def add(self, relpath, title):
        _log.debug("Add %s as %s", relpath, title)
        self.items.append(
            self.Item(
                title=title,
                path=relpath,
            )
        )

    def page(self):
        return "<ul>{}</ul>".format(
            "".join(
                """<li><a href="/{path}">{title}</a></li>""".format(
                    path=item.path,
                    title=item.title,
                )
                for item in self.items
            )
        ).encode("utf-8")


class DataNode(INode):
    def __init__(self, path):
        self.path = path
        self.title_ = os.path.basename(path)
        (self.mime_type_, self.encoding_) = mimetypes.guess_type(path, strict=True)

    def page(self):
        with open(self.path, "rb") as fin:
            return fin.read()


def skip_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def build_tree(root_path):
    tree = dict()
    for (dirpath, dirnames, filenames) in os.walk(root_path, followlinks=True):
        if os.path.basename(dirpath).startswith("."):
            continue
        map_node = MapNode(dirpath)
        for filename in filenames:
            if filename.startswith("."):
                continue
            filepath = os.path.join(dirpath, filename)
            relpath = skip_prefix(filepath, root_path)
            extension = os.path.splitext(relpath)[1]
            if extension in MdNode.ACCEPTED_EXTENSIONS:
                node = MdNode(filepath)
            else:
                node = DataNode(filepath)
            tree[relpath] = node
            map_node.add(relpath, node.title())

        for dirname in dirnames:
            if dirname.startswith("."):
                continue
            relpath = skip_prefix(
                os.path.join(dirpath, dirname),
                root_path,
            )
            map_node.add(relpath, os.path.basename(relpath))
        relpath = skip_prefix(dirpath, root_path)
        tree[relpath] = map_node
    return tree


class QueryHandler(http.server.BaseHTTPRequestHandler):
    tree = None

    def do_GET(self):
        node = self.tree.get(
            self.path.strip("/")
        )
        if node is None:
            self._error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", node.content_type())
        self.send_header("Content-encoding", node.content_encoding())
        self.end_headers()
        self.wfile.write(
            node.page()
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
    tree = build_tree(args.dir)
    run_server(tree, args.hostname, args.port)


if __name__ == "__main__":
    try:
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
