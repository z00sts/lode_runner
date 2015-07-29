# -*- coding: utf-8 -*-
import unittest
import optparse
import sys
from xml.etree import ElementTree

import os
import re
from nose.config import Config
from lode_runner.plugins.xunit import Xunit

time_taken = re.compile(r'\d\.\d\d')


test_name = u"runTest_фыва"


def mktest():
    global test_name
    class TestCase(unittest.TestCase):
        pass
    if not isinstance(test_name, str):
        setattr(TestCase, test_name.encode("utf8"), lambda x: x.assertTrue(True))
    else:
        setattr(TestCase, test_name, lambda x: x.assertTrue(True))
    test = TestCase(methodName="runTest_фыва")
    return test


class XunitTest(unittest.TestCase):
    def setUp(self):
        self.xmlfile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'xunit.xml'))
        parser = optparse.OptionParser()
        self.x = Xunit()
        self.x.add_options(parser, env={})
        (options, args) = parser.parse_args([
            "--with-xunit",
            "--xunit-file=%s" % self.xmlfile
        ])
        self.x.configure(options, Config())

    def tearDown(self):
        try:
            os.remove(self.xmlfile)
        except OSError:
            pass

    def test_with_unicode_string_in_output(self):
        a = "тест"
        b = u'тест'
        print(a, b)
        self.assertTrue(True)

    def get_xml_report(self):
        class DummyStream:
            pass
        self.x.report(DummyStream())
        f = open(self.xmlfile, 'rb')
        data = f.read()
        f.close()
        return data

    def test_addFailure(self):
        test = mktest()
        self.x.beforeTest(test)
        message = u"%s is not 'equal' to %s" % (u'Тест', u'тест')
        try:
            raise AssertionError(message)
        except AssertionError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        some_err = (ec, ev.args[0], tb)

        self.x.addFailure(test, some_err)

        result = self.get_xml_report()

        tree = ElementTree.fromstring(result)
        self.assertEqual(tree.attrib['name'], "nosetests")
        self.assertEqual(tree.attrib['tests'], "1")
        self.assertEqual(tree.attrib['errors'], "0")
        self.assertEqual(tree.attrib['failures'], "1")
        self.assertEqual(tree.attrib['skip'], "0")

        tc = tree.find("testcase")
        self.assertEqual(tc.attrib['classname'], "test_xunit.TestCase")
        self.assertEqual(tc.attrib['name'], test_name)
        assert time_taken.match(tc.attrib['time']), (
                    'Expected decimal time: %s' % tc.attrib['time'])

        err = tc.find("failure")
        self.assertEqual(err.attrib['type'], "%s.AssertionError" % (AssertionError.__module__,))
        err_lines = err.text.strip().split("\n")
        self.assertEqual(err_lines[-1], message)
        self.assertEqual(err_lines[-2], '    raise AssertionError(message)')

    def test_addError(self):
        test = mktest()
        self.x.beforeTest(test)
        message = u"%s is not 'equal' to %s" % (u'Тест', u'тест')
        try:
            raise RuntimeError(message)
        except RuntimeError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        some_err = (ec, ev.args[0], tb)

        self.x.addError(test, some_err)

        result = self.get_xml_report()

        tree = ElementTree.fromstring(result)
        self.assertEqual(tree.attrib['name'], "nosetests")
        self.assertEqual(tree.attrib['tests'], "1")
        self.assertEqual(tree.attrib['errors'], "1")
        self.assertEqual(tree.attrib['failures'], "0")
        self.assertEqual(tree.attrib['skip'], "0")

        tc = tree.find("testcase")
        self.assertEqual(tc.attrib['classname'], "test_xunit.TestCase")
        self.assertEqual(tc.attrib['name'], test_name)
        assert time_taken.match(tc.attrib['time']), (
                    'Expected decimal time: %s' % tc.attrib['time'])

        err = tc.find("error")
        self.assertEqual(err.attrib['type'], "%s.RuntimeError" % (RuntimeError.__module__,))
        err_lines = err.text.strip().split("\n")
        self.assertIn(message, err_lines[-1])
        self.assertEqual(err_lines[-2], '    raise RuntimeError(message)')
