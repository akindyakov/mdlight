#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All about index pages are here
"""

import logging
import mimetypes
import os
import re
import subprocess


_log = logging.getLogger(__name__)


class IPage(object):
    mime_type_ = "text/html;charset=utf-8"
    encoding_ = None
    title_ = None

    def content_type(self):
        return self.mime_type_

    def content_encoding(self):
        return self.encoding_

    def title(self):
        return self.title_


class MarkdownPage(IPage):
    RE_FIRST_HEADER = re.compile("\s*#([^#].*)")
    @staticmethod
    def _extract_title(pathname):
        title = os.path.basename(pathname)
        if not os.path.isdir(pathname):
            with open(pathname) as fin:
                for (num, line) in enumerate(fin):
                    if num > 10:
                        break
                    m = MarkdownPage.RE_FIRST_HEADER.match(line)
                    if m:
                        title += ": " + m.groups()[0].strip()
                        break
        return title

    ACCEPTED_EXTENSIONS = {".markdown", ".md", ".tex"}
    BINARY_NAME = "pandoc"

    def __init__(self, filepath):
        _log.debug("Markdown node %r", filepath)
        self.filepath = filepath
        self.title_ = self._extract_title(filepath)
        self.encoding_ = "identity"

    def content(self):
        proc = subprocess.Popen(
            [self.BINARY_NAME, self.filepath, "--to", "html5"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        text = proc.stdout.read()
        proc.wait()
        return text


class GraphvizPage(IPage):
    ACCEPTED_EXTENSIONS = {
        ".graphviz",
        ".dot",
    }
    BINARY_NAME = "dot"

    def __init__(self, filepath):
        _log.debug("Graphviz node %r", filepath)
        self.filepath = filepath
        self.title_ = os.path.basename(filepath)
        self.mime_type_ = "image/svg+xml"

    def content(self):
        proc = subprocess.Popen(
            [self.BINARY_NAME , self.filepath, "-T", "svg"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        text = proc.stdout.read()
        proc.wait()
        return text


class IndexPage(IPage):
    class Item(object):
        def __init__(self, title, path):
            self.title = title
            self.path = path

    def __init__(self, path):
        _log.debug("Index page %r", path)
        self.path = path
        self.items = list()
        self.title_ = os.path.basename(path)

    def add(self, relpath, title):
        _log.debug("Add %s as %s", relpath, title)
        self.items.append(
            self.Item(
                title=title,
                path=relpath,
            )
        )

    def content(self):
        return "<ul>{}</ul>".format(
            "".join(
                """<li><a href="/{path}">{title}</a></li>""".format(
                    path=item.path,
                    title=item.title,
                )
                for item in self.items
            )
        ).encode("utf-8")


class StaticPage(IPage):
    def __init__(self, path):
        _log.debug("Static page %r", path)
        self.path = path
        self.title_ = os.path.basename(path)
        (self.mime_type_, self.encoding_) = mimetypes.guess_type(path, strict=True)

    def content(self):
        with open(self.path, "rb") as fin:
            return fin.read()
