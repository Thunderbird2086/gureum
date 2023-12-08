"""
Generate a emoji.txt from a emoji-test.txt
"""
from typing import Iterable
import xml.etree.ElementTree as ET
import logging

import unittest
import requests


data = []


def generate_ko_emoji(files):
    lines = []
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        for annotation in root.iter('annotation'):
            emoji = annotation.get('cp')
            tags = annotation.text
            for tag in tags.split('|'):
                tag = _refine_description(tag.strip())
                lines.append((emoji, tag))
    lines = list(set(lines))
    lines.sort(key=lambda x: (x[1], x[0]))

    with open('emoji_ko.txt', 'w') as f:
        for emoji, desc in lines:
            f.write(f'{desc}:{emoji}:{desc}\n')


def make_emoji(filename: str = 'generate_emoji.txt') -> int:
    global data

    with open(filename, 'r', encoding='utf-8') as file:
        file_lines = file.readlines()

    qualified_lines = _get_fully_qualified_lines(file_lines)

    for line in qualified_lines:
        data.append(_get_emoji_data(line))


def generate_emoji(filename: str = 'emoji-test.txt') -> int:
    """generate emoji from input file

    Args:
        Input filename
    Return:
        Number of written characters
    """
    global data

    with open(filename, 'r', encoding='utf-8') as file:
        file_lines = file.readlines()

    qualified_lines = _get_fully_qualified_lines(file_lines)

    for line in qualified_lines:
        data.append(_get_emoji_data(line))

    data.sort()  # XXX: search uses binary search algorithm

    with open('emoji.txt', 'w') as file:
        for desc, _, emoji in data:
            num = file.write('{1}:{0}:{1}\n'.format(emoji, desc))

    return num


def _get_fully_qualified_lines(lines: list) -> Iterable[str]:
    """Get lines with fully qualified as a iterable"""
    return (l for l in lines if _is_valid_line(l))


def _is_valid_line(line: str) -> bool:
    """Check if the line is fully qualified"""
    if line.startswith('#'):
        return False
    if line.startswith('\n'):
        return False
    if 'non-fully-qualified' in line:
        return False
    return True


def _get_emoji_data(line: str) -> tuple:
    """Extract the emoji data from a line

    Args:
        a fully-qualified line
    Return:
        Description, Unicode, emoji
    """
    data = line.split('; fully-qualified')

    unicode = data[0].strip()

    bytes_num = len(unicode.split())
    emoji = data[1].strip()[2:]

    desc = emoji[bytes_num+1:]
    emoji = emoji[0:bytes_num]

    desc = _refine_description(desc)

    return desc, unicode, emoji


def _refine_description(desc):
    """Refines a description

    1. Not to use colon in description
    """
    desc = desc.replace(':', ';')
    return desc


class TestGenerateemoji(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_non_fully_qualified_line(self):
        line = '263A                                       ; non-fully-qualified # ☺ smiling face'
        self.assertFalse(_is_valid_line(line))

    def test_empty_line(self):
        line = '\n'
        self.assertFalse(_is_valid_line(line))

    def test_comment_line(self):
        line = '# subgroup: face-negative'
        self.assertFalse(_is_valid_line(line))

    def test_get_emoji_data(self):
        lines = [
            '1F62F                                      ; fully-qualified     # 😯 hushed face',
            '2620 FE0F                                  ; fully-qualified     # ☠️ skull and crossbones',
            '1F469 1F3FC                                ; fully-qualified     # 👩🏼 woman: medium-light skin tone',
            '1F469 200D 2695 FE0F                       ; fully-qualified     # 👩‍⚕️ woman health worker',
            '1F3CA 1F3FB 200D 2642 FE0F                 ; fully-qualified     # 🏊🏻‍♂️ man swimming: light skin tone',
        ]

        desc, unicode, emoji = _get_emoji_data(lines[0])
        self.assertEqual(unicode, '1F62F')
        self.assertEqual(emoji, '😯')
        self.assertEqual(desc, 'hushed face')
        desc, unicode, emoji = _get_emoji_data(lines[1])
        self.assertEqual(unicode, '2620 FE0F')
        self.assertEqual(emoji, '☠️')
        self.assertEqual(desc, 'skull and crossbones')
        desc, unicode, emoji = _get_emoji_data(lines[2])
        self.assertEqual(unicode, '1F469 1F3FC')
        self.assertEqual(emoji, '👩🏼')
        self.assertEqual(desc, 'woman; medium-light skin tone')
        desc, unicode, emoji = _get_emoji_data(lines[3])
        self.assertEqual(unicode, '1F469 200D 2695 FE0F')
        self.assertEqual(emoji, '👩‍⚕️')
        self.assertEqual(desc, 'woman health worker')
        desc, unicode, emoji = _get_emoji_data(lines[4])
        self.assertEqual(unicode, '1F3CA 1F3FB 200D 2642 FE0F')
        self.assertEqual(emoji, '🏊🏻‍♂️')
        self.assertEqual(desc, 'man swimming; light skin tone')


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


if __name__ == '__main__':
    tag = 'release-44-1'
    ko_url = f"https://raw.githubusercontent.com/unicode-org/cldr/{tag}/common/annotations/ko.xml"
    ko_d_url = f"https://raw.githubusercontent.com/unicode-org/cldr/{tag}/common/annotationsDerived/ko.xml"

    download(ko_url, f"ko_annotations.{tag}.xml")
    download(ko_d_url, f"ko_annotations_derived.{tag}.xml")

    ko_emoji_files = [f'ko_annotations.{tag}.xml', f'ko_annotations_derived.{tag}.xml']
    generate_ko_emoji(ko_emoji_files)

    unittest.main(exit=False)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s'
    )

    try:
        make_emoji()
        generate_emoji()
        logging.info('emoji.txt has been created')
    except Exception as e:
        logging.error(e)
