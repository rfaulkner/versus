# -*- coding: utf-8 -*-

"""
dynamic_learn.testsuite
~~~~~~~~~~~~~~~~~~~~~~~

:license: BSD, see LICENSE for more details.
"""

import unittest

from versus.tools.dataIO import DataIORedis


class LocalTestCase(unittest.TestCase):
    """
    Setup relevant test context in this class
    """
    def setUp(self):
        # TODO - add setup for MySQLIO related testing
        unittest.TestCase.setUp(self)


class TestMySQLConnect(LocalTestCase):
    """ Test cases for Redis read/writes """

    def test_simple(self):
        raise NotImplementedError()


class TestMySQLCreateTable(LocalTestCase):
    """ Test cases for Redis read/writes """

    def test_simple(self):
        raise NotImplementedError()
