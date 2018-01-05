#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All about index tree are here
"""

import logging
import os
import re

import index.pages as pages


_log = logging.getLogger(__name__)


def _skip_path_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    if string.startswith("/"):
        string = string[1:]
    return string


_RE_HIDDEN_PATH = re.compile("(./|^)\.[^\./]")


def _is_hidden_path(path):
    to_skip = _RE_HIDDEN_PATH.match(path) is not None
    return to_skip


def build_tree(root_path):
    tree = dict()
    for (dirpath, dirnames, filenames) in os.walk(root_path, followlinks=True):
        if _is_hidden_path(dirpath):
            continue
        map_node = pages.IndexPage(dirpath)
        for filename in filenames:
            if _is_hidden_path(filename):
                continue
            filepath = os.path.join(dirpath, filename)
            relpath = _skip_path_prefix(filepath, root_path)
            extension = os.path.splitext(relpath)[1]
            if extension in pages.MarkdownPage.ACCEPTED_EXTENSIONS:
                node = pages.MarkdownPage(filepath)
            else:
                node = pages.StaticPage(filepath)
            tree[relpath] = node
            map_node.add(relpath, node.title())

        for dirname in dirnames:
            if _is_hidden_path(dirname):
                continue
            relpath = _skip_path_prefix(
                os.path.join(dirpath, dirname),
                root_path,
            )
            map_node.add(relpath, os.path.basename(relpath))
        relpath = _skip_path_prefix(dirpath, root_path)
        tree[relpath] = map_node
    return tree
