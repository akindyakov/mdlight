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
        page = pages.IndexPage(abs_path)
        for file_base_name in os.listdir(abs_path):
            abs_file_path = os.path.join(abs_path, file_base_name)
            relative_file_path = os.path.join(relative_path, file_base_name)
            if not _is_hidden_path(abs_file_path):
                page.add(
                    relative_file_path,
                    _create_node_rec(
                        abs_file_path,
                        relative_file_path,
                    ).title(),
                )
    else:
        extension = os.path.splitext(abs_path)[1]
        if extension in pages.MarkdownPage.ACCEPTED_EXTENSIONS:
            page = pages.MarkdownPage(abs_path)
        elif extension in pages.GraphvizPage.ACCEPTED_EXTENSIONS:
            page = pages.GraphvizPage(abs_path)
        else:
            page = pages.StaticPage(abs_path)
    return page


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
