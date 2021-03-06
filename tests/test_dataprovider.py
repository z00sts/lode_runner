# -*- coding: utf-8 -*-
from collections import namedtuple
import unittest

from lode_runner.plugins.dataprovider import dataprovider

tests_to_run = [
    "test_data_dataprovider_1",
    "test_data_dataprovider_2",
    "test_data_dataprovider_3",
    "test_method_dataprovider_1",
    "test_method_dataprovider_2",
    "test_method_dataprovider_3",
    "test_function_dataprovider_1",
    "test_function_dataprovider_2",
    "test_function_dataprovider_3",
    u"test_unicode_string_dataprovider_Первый Тест",
    u"test_unicode_string_dataprovider_Второй Тест",
    "test_single_dataprovider_('.1', u'/2')",
    "test_class_dataprovider_1",
    "test_class_dataprovider_2",
    "test_class_dataprovider_3",
    u"test_dict_dataprovider_{'one': u'первый тест', 'two': u'второй тест'}",
    u"test_list_dataprovider_[u'первый тест', u'второй тест']",
    u"test_tuple_dataprovider_(u'первый тест', u'второй тест')",
    u"test_namedtuple_dataprovider_({'one': u'первый тест', 'two': u'второй тест'})",
]


def function_provider():
    return [1, 2, 3]


class DataproviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.set_up_class_called = True

    def setUp(self):
        self.set_up_called = True

    @dataprovider([1, 2, 3])
    def test_data_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_data_dataprovider", data))

    @classmethod
    def value(cls):
        return 1

    @classmethod
    def method_provider(cls):
        value = cls.value()
        return [(x + value) for x in (0, 1, 2)]

    @dataprovider(method_provider)
    def test_method_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_method_dataprovider", data))

    @dataprovider(function_provider)
    def test_function_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_function_dataprovider", data))

    @dataprovider([u'Первый Тест', u"Второй Тест"])
    def test_unicode_string_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_unicode_string_dataprovider", data))

    @dataprovider([1])
    def test_setup_runs(self, data):
        self.assertTrue(self.set_up_called)
        self.assertTrue(self.set_up_class_called)


class SingleDataproviderTest(unittest.TestCase):
    @dataprovider([
        ('.1', u'/2'),
    ])
    def test_single_dataprovider(self, data1, data2):
        tuple_string = "('%s', u'%s')" % (data1, data2)
        test_name = "%s_%s" % ("test_single_dataprovider", tuple_string)
        tests_to_run.remove(test_name)


class NestedDataprovidersTest(unittest.TestCase):
    @dataprovider([[u'первый тест', u'второй тест']])
    def test_list_dataprovider(self, data):
        list_string = "[u'%s', u'%s']" % (data[0], data[1])
        test_name = "%s_%s" % ("test_list_dataprovider", list_string)
        tests_to_run.remove(test_name)

    @dataprovider([{'one': u'первый тест', 'two': u'второй тест'}])
    def test_dict_dataprovider(self, data):
        l = sorted(iter(data.items()))
        key1, value1 = l[0]
        key2, value2 = l[1]
        dict_string = "{'%s': u'%s', '%s': u'%s'}" % (key1, value1, key2, value2)
        test_name = "%s_%s" % ("test_dict_dataprovider", dict_string)
        tests_to_run.remove(test_name)

    @dataprovider([(u'первый тест', u'второй тест')])
    def test_tuple_dataprovider(self, first, second):
        tuple_string = "(u'%s', u'%s')" % (first, second)
        tests_to_run.remove("%s_%s" % ("test_tuple_dataprovider", tuple_string))

    NamedTuple = namedtuple('NamedTuple', 'one two')
    @dataprovider([(NamedTuple(u'первый тест', u'второй тест'),)])
    def test_namedtuple_dataprovider(self, data):
        l = list(iter(data._asdict().items()))
        key1, value1 = l[0]
        key2, value2 = l[1]
        dict_string = "{'%s': u'%s', '%s': u'%s'}" % (key1, value1, key2, value2)
        test_name = "%s_(%s)" % ("test_namedtuple_dataprovider", dict_string)
        tests_to_run.remove(test_name)


@dataprovider([1, 2, 3])
class ClassDataproviderTest(unittest.TestCase):
    def test_class_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_class_dataprovider", data))


class TestAllTestsRan(unittest.TestCase):
    def test_all_tests_ran(self):
        self.assertEqual([], tests_to_run)
