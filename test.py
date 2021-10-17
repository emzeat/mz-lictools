import license_tools
import unittest
import pathlib

BASE = pathlib.Path(__file__).parent


class TestParserCStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.1author_1year.h')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.1author_2years.cxx')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.2authors_2years.c')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestParserPoundStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.1author_1year.py')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.1author_2years.sh')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/Parser.2authors_2years')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestLicense(unittest.TestCase):

    def test_generator(self):
        author1 = license_tools.Author('Max Muster', 2013, 2020)
        author2 = license_tools.Author('Umbrella Inc', 2021)
        authors = [author1, author2]

        for l in license_tools.LICENSES:
            license = license_tools.License(l)
            header = license_tools.Header(license)
            filename = f'TestLicense.c_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.C_STYLE)
            with open(BASE / 'test' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)
            filename = f'TestLicense.pound_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.POUND_STYLE)
            with open(BASE / 'test' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)


if __name__ == '__main__':
    unittest.main()
