#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from mdlight.index import tree


def test__skip_path_prefix():
    assert "" == tree._skip_path_prefix("", "")
    assert "" == tree._skip_path_prefix("/", "")
    assert "" == tree._skip_path_prefix("./", ".")
    assert "out/of/bed" == tree._skip_path_prefix("/i/stumbled/out/of/bed", "/i/stumbled")
    assert "for/the/struggle" == tree._skip_path_prefix("./i/got/ready/for/the/struggle", "./i/got/ready/")
    assert "i/smoked/a/cigarette" == tree._skip_path_prefix("../../i/smoked/a/cigarette", "../../")
    assert "up/my/gut" == tree._skip_path_prefix("./../../and/i/tightened/up/my/gut", "./../../and/i/tightened/")

    with pytest.raises(tree.WrongPath):
        assert "" == tree._skip_path_prefix("i/said/this/can", "t/be/me")


def test__is_hidden_path():
    assert False == tree._is_hidden_path("")
    assert False == tree._is_hidden_path("/")
    assert False == tree._is_hidden_path(".")
    assert False == tree._is_hidden_path("../.")
    assert False == tree._is_hidden_path("/everybody/knows")
    assert False == tree._is_hidden_path("that/the/dice/are/loaded")
    assert False == tree._is_hidden_path("/everybody/rolls/with.their/fingers.crossed")
    assert False == tree._is_hidden_path("./the/war/is/over")
    assert False == tree._is_hidden_path("./the/good/../guys/lost.")
    assert False == tree._is_hidden_path("./the//fight/was/./fixed")
    assert True == tree._is_hidden_path("./the/poor/.stay/poor")
    assert True == tree._is_hidden_path("the/rich/get/.rich")
    assert True == tree._is_hidden_path("/that.s/how/it/.goes")
    assert True == tree._is_hidden_path(".everybody/knows")
