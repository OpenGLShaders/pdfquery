from lxml import etree

from six import BytesIO
import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

class BaseTestCase(unittest.TestCase):

    def assertValidOutput(self, pdf, output_name):
        """
            Test that converted XML hasn't changed from saved version.
        """
        # Just skip this test if we're on python 2.6 -- float handling makes element sort ordering unpredictable,
        # causing intermittent test failures.
        if sys.version_info[:2] < (2, 7):
            return

        # get current XML for sample file
        tree_string = BytesIO()
        pdf.tree.write(tree_string, pretty_print=True, encoding="utf-8")
        tree_string = tree_string.getvalue()

        # get previous XML
        # this varies by Python version, because the float handling isn't quite
        # the same
        comparison_file = "tests/saved_output/%s.xml" % (output_name,)
        with open(comparison_file, 'rb') as f:
            saved_string = f.read()

        # compare current to previous
        try:
            self.xml_strings_equal(saved_string, tree_string)
        except self.failureException as e:
            output_path = "tests/%s_failed_output.xml" % output_name
            with open(output_path, "wb") as out:
                out.write(tree_string)
            raise self.failureException("XML conversion of sample pdf has changed! Compare %s to %s" % (comparison_file, output_path)) from e

    def xml_strings_equal(self, s1, s2):
        """
            Return true if two xml strings are semantically equivalent (ignoring attribute ordering and whitespace).
        """
        # via http://stackoverflow.com/a/24349916/307769
        def elements_equal(e1, e2):
            if e1.tag != e2.tag: raise self.failureException("Mismatched tags")
            if e1.text != e2.text: raise self.failureException("Mismatched text")
            if e1.tail != e2.tail: raise self.failureException("Mismatched tail")
            if e1.attrib != e2.attrib: raise self.failureException("Mismatched attributes")
            if len(e1) != len(e2): raise self.failureException("Mismatched children")
            for c1, c2 in zip(e1, e2):
                elements_equal(c1, c2)

        e1 = etree.XML(s1, parser=etree.XMLParser(remove_blank_text=True))
        e2 = etree.XML(s2, parser=etree.XMLParser(remove_blank_text=True))

        return elements_equal(e1, e2)
