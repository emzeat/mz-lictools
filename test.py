import license_tools
import unittest
import pathlib

BASE = pathlib.Path(__file__).parent


class TestParserCStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-1author_1year.h')
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
            file=BASE / 'test/TestParserCStyle-1author_2years.cxx')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-2authors_2years.c')
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
            file=BASE / 'test/TestParserPoundStyle-1author_1year.py')
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
            file=BASE / 'test/TestParserPoundStyle-1author_2years.sh')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserPoundStyle-2authors_2years')
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


class TestHeader(unittest.TestCase):

    def test_generator(self):
        author1 = license_tools.Author('Max Muster', 2013, 2020)
        author2 = license_tools.Author('Umbrella Inc', 2021)
        authors = [author1, author2]

        for l in license_tools.LICENSES:
            license = license_tools.License(l)
            header = license_tools.Header(license)
            filename = f'TestHeader-c_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.C_STYLE)
            with open(BASE / 'test' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)
            filename = f'TestHeader-pound_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.POUND_STYLE)
            with open(BASE / 'test' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)


class TestTool(unittest.TestCase):

    def test_bump(self):
        author = license_tools.Author("Test Guy")
        license = license_tools.License("Apache")
        tool = license_tools.Tool(
            default_license=license, default_author=author)
        for file in BASE.glob('test/TestTool-bump*.input.*'):
            stem = file.name.split('.')[0]
            result = tool.bump(file, keep_license=True)
            self.assertIsNotNone(result)
            with open(BASE / 'test' / (stem + ".expected"), 'r') as expected:
                self.assertEqual(expected.read(), result)


if __name__ == '__main__':
    unittest.main()
