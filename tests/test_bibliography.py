import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from bibtex import parse, publications, plain, author_names, BibTeXError
from build import inline, citation, safe_url


class BibliographyTests(unittest.TestCase):
    def test_scholar_export_nested_and_quoted_fields(self):
        rows = publications(r'''@article{key,
            title={{DNA}: A {Graph, Nested} Study},
            author={Nguyen-Vo, Thanh-Hoang and Doe, Jane},
            year={2026}, journal="Journal of {Computing}",
            doi={10.1234/test}, keywords={Bioinformatics, Deep Learning}}
        ''')
        self.assertEqual(rows[0]['title'],'DNA: A Graph, Nested Study')
        self.assertEqual(rows[0]['authors'],'Thanh-Hoang Nguyen-Vo, Jane Doe')
        self.assertEqual(rows[0]['topics'],['Bioinformatics','Deep Learning'])

    def test_string_macros_and_concatenation(self):
        entries = parse('@string{j="Journal"}\n@article(k,title={A},year=2025,journal=j # { of Science})')
        self.assertEqual(entries[0]['journal'],'Journal of Science')

    def test_crossref_inheritance_and_cycles(self):
        entries = parse('@inproceedings{c,title={Child},crossref={p}}\n@proceedings{p,title={Parent},year=2024,booktitle={Conference}}')
        self.assertEqual(entries[0]['title'],'Child')
        self.assertEqual(entries[0]['year'],'2024')
        with self.assertRaises(BibTeXError):
            parse('@book{a,title={A},crossref={b}} @book{b,title={B},crossref={a}}')

    def test_malformed_export_does_not_publish_partial_data(self):
        for text in ['@article{k,title={Unclosed}', '@article{k,title={A} year=2024}', '@article{k,title=undefined}', '@article{k,title={A}} @article{k,title={B}}']:
            with self.subTest(text=text),self.assertRaises(BibTeXError): parse(text)

    def test_unpublished_records_are_excluded(self):
        result = publications('''@article{p,title={Published},year=2024,journal={Journal}}
        @article{a,title={Not published},year=2026,journal={arXiv preprint arXiv:123}}
        @article{s,title={Submitted},year=2026,journal={Journal},status={submitted}}
        @misc{m,title={Preprint},year=2026}''')
        self.assertEqual([r['key'] for r in result],['p'])

    def test_duplicate_doi_is_case_insensitive(self):
        result = publications('''@article{a,title={A},year=2024,journal={J},doi={https://doi.org/10.1234/ABC}}
        @article{b,title={B},year=2024,journal={J},doi={10.1234/abc}}''')
        self.assertEqual(len(result),1)

    def test_missing_publication_details_fail(self):
        with self.assertRaises(BibTeXError): publications('@article{a,title={A},year={2026}}')
        with self.assertRaises(BibTeXError): publications('@article{a,title={A},year={no},journal={J}}')

    def test_diacritics_and_corporate_authors(self):
        self.assertEqual(plain(r"{Garc\'{i}a} and M{\"u}ller"),'García and Müller')
        self.assertEqual(author_names('{Research and Development Group} and Doe, Jane'),'Research and Development Group, Jane Doe')

    def test_untrusted_content_is_escaped(self):
        self.assertIn('&lt;script&gt;',inline('<script>alert(1)</script>'))
        with self.assertRaises(ValueError): inline('[click](javascript:alert)')
        with self.assertRaises(ValueError): safe_url('//attacker.test')
        with self.assertRaises(ValueError): safe_url('javascript:alert(1)')
        row = publications('@article{a,title={<img src=x onerror=alert(1)>},year=2026,journal={J}}')[0]
        self.assertNotIn('<img',citation(row))


if __name__=='__main__': unittest.main()
