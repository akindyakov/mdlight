#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All about index tree are here
"""

import logging
import os
import re

from mdlight.index import pages


_log = logging.getLogger(__name__)


class TreeError(RuntimeError):
    pass


class WrongPath(TreeError):
    pass


def _skip_path_prefix(path, prefix):
    if not path.startswith(prefix):
        raise WrongPath(
            "There is no such prefix {pref!r} in the path {path!r}".format(
                pref=prefix,
                path=path,
            )
        )
    path = path[len(prefix):]
    if path.startswith("/"):
        path = path[1:]
    return path


_RE_HIDDEN_PATH = re.compile(".*(./|^)\.[^\./]")


def _is_hidden_path(path):
    to_skip = _RE_HIDDEN_PATH.match(path) is not None
    return to_skip


def _create_node_rec(abs_path, relative_path):
    if os.path.isdir(abs_path):
        return IndexPage(abs_path, relative_path)
    else:
        extension = os.path.splitext(abs_path)[1]
        if extension in pages.MarkdownPage.ACCEPTED_EXTENSIONS:
            return pages.MarkdownPage(abs_path)
        elif extension in pages.GraphvizPage.ACCEPTED_EXTENSIONS:
            return pages.GraphvizPage(abs_path)
        else:
            return pages.StaticPage(abs_path)


class IndexPage(pages.IPage):
    class Item(object):
        def __init__(self, title, path):
            self.title = title
            self.path = path

    def __init__(self, abs_path, relative_path):
        _log.debug("Index page %r", relative_path)
        self.abs_path = abs_path
        self.relative_path = relative_path
        self.title_ = os.path.basename(abs_path)

    def content(self):
        items = list()
        for file_base_name in os.listdir(self.abs_path):
            abs_file_path = os.path.join(self.abs_path, file_base_name)
            relative_file_path = os.path.join(self.relative_path, file_base_name)
            if _is_hidden_path(abs_file_path):
                continue
            items.append(
                self.Item(
                    _create_node_rec(
                        abs_file_path,
                        relative_file_path,
                    ).title(),
                    relative_file_path,
                )
            )
        items.sort(
            key=lambda item: item.title
        )
        return "<h2>{title}</h2> <ul>{ls}</ul>".format(
            title=self.title(),
            ls="".join(
                """<li><a href="/{path}">{title}</a></li>""".format(
                    path=item.path,
                    title=item.title,
                )
                for item in items
            )
        ).encode("utf-8")


def create_node(root_path, relative_path):
    abs_path = os.path.realpath(
        os.path.join(root_path, relative_path)
    )
    if not os.path.exists(abs_path):
        raise WrongPath(
            "There is no such file {path!r}".format(
                path=relative_path,
            )
        )
    relative_path = _skip_path_prefix(abs_path, root_path)
    if _is_hidden_path(abs_path):
        raise WrongPath(
            "The path {path!r} is hidden".format(
                path=abs_path,
            )
        )
    return _create_node_rec(abs_path, relative_path)
