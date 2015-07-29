# coding: utf-8

import multiprocessing
from functools import partial

from xml.etree import ElementTree
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from nose.plugins.xunit import Xunit, force_unicode
from nose.plugins.base import Plugin


MANAGER = multiprocessing.Manager()
MP_ERRORLIST = MANAGER.list()
MP_STATS = MANAGER.dict({
    'errors': 0,
    'failures': 0,
    'passes': 0,
    'skipped': 0})


class Xunit(Xunit):
    def configure(self, options, config):
        """Configures the xunit plugin."""
        Plugin.configure(self, options, config)
        self.config = config
        if self.enabled:
            if hasattr(options, 'multiprocess_workers') and options.multiprocess_workers:
                self.stats = MP_STATS
                self.errorlist = MP_ERRORLIST
            else:
                super(Xunit, self).configure(options, config)

        self.error_report_filename = options.xunit_file

    def report(self, stream):
        """Writes an Xunit-formatted XML file

        The file includes a report of test errors and failures.

        """
        self.stats['encoding'] = self.encoding
        self.stats['total'] = (self.stats['errors'] + self.stats['failures']
                               + self.stats['passes'] + self.stats['skipped'])
        testsuite = ElementTree.Element("testsuite", attrib={
            "name": "nosetests",
            "tests": str(self.stats['total']),
            "errors": str(self.stats['errors']),
            "failures": str(self.stats['failures']),
            "skip": str(self.stats['skipped']),
        })
        errors = [force_unicode(error) for error in self.errorlist]
        [testsuite.append(ElementTree.fromstring(error.encode("utf-8"))) for error in errors]
        ElementTree.ElementTree(testsuite).write(self.error_report_filename, encoding="utf-8", xml_declaration=True)

        if self.config.verbosity > 1:
            stream.writeln("-" * 70)
            stream.writeln("XML: %s" % self.error_report_filename)

    def beforeTest(self, test):
        """Initializes a timer before starting a test."""
        test.id = partial(force_unicode, test.id())
        super(Xunit, self).beforeTest(test)
