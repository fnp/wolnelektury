import doctest
import unittest
import catalogue.models.book


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(catalogue.models.book))
    return tests
