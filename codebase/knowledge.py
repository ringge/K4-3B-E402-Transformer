"""Page-preserving extraction and deterministic local retrieval; no network."""
from dataclasses import asdict, dataclass
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import math
import re
import unicodedata


def normalize(text):
    text = unicodedata.normalize('NFD', text.lower().replace('đ', 'd'))
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


STOP = set('la va cua mot nhung cai nay do thi ma toi minh ban gi sao nhu the nao khong hieu van chua giai thich lai cho duoc trang day'.split())

# Preserve source text for inspection, but do not teach disputed wording as fact.
SOURCE_FLAGS = {
    'D1-P015-B006': 'Câu về attention và chữ T trong GPT có diễn đạt dễ gây hiểu sai; cần TA kiểm tra. Không dùng câu này làm định nghĩa.',
}


def tokens(text):
    return set(re.findall(r'[a-z0-9_]+', normalize(text))) - STOP


@dataclass(frozen=True)
class Page:
    source_id: str
    file_page: int
    anchor: str
    title: str
    blocks: tuple[str, ...]

    @property
    def text(self):
        return '\n'.join(self.blocks)

    def evidence(self):
        return {'source_id': self.source_id, 'title': self.title,
                'blocks': [{'id': f'{self.source_id}-B{i:03}', 'text': s}
                           for i, s in enumerate(self.blocks, 1) if f'{self.source_id}-B{i:03}' not in SOURCE_FLAGS],
                'warnings': [note for key,note in SOURCE_FLAGS.items() if key.startswith(self.source_id+'-B')]}


class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pages = []
        self.page = None
        self.parts = []
        self.blocks = []
        self.headings = []
        self.heading = None
        self.heading_parts = []
        self.ignored = 0

    def flush(self):
        text = re.sub(r'\s+', ' ', ''.join(self.parts)).strip()
        self.parts = []
        if text and not re.fullmatch(r'FilePage \d+|AI IN ACTION\s*[-–·]?\s*(HACKATHON|Day 1)', text, re.I):
            self.blocks.append(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section' and 'data-file-page' in a:
            self.page = int(a['data-file-page'])
            self.anchor = a.get('id', f'p{self.page}')
            self.parts, self.blocks, self.headings = [], [], []
        if self.page is None:
            return
        if tag in {'script', 'style'}:
            self.ignored += 1
        if tag in {'p', 'li', 'tr', 'h1', 'h2', 'h3', 'figcaption'}:
            self.flush()
        if tag in {'h1', 'h2', 'h3'}:
            self.heading, self.heading_parts = tag, []
        if tag == 'br':
            self.parts.append(' ')
        if tag in {'td', 'th'} and self.parts:
            self.parts.append(' | ')
        if tag == 'img' and a.get('alt', '').strip() and a.get('data-role') != 'decorative':
            self.flush()
            self.blocks.append('[Mô tả ảnh trong HTML; chưa xác minh hình ảnh] ' + a['alt'])

    def handle_data(self, data):
        if self.page is not None and not self.ignored:
            self.parts.append(data)
            if self.heading:
                self.heading_parts.append(data)

    def handle_endtag(self, tag):
        if self.page is None:
            return
        if tag in {'script', 'style'}:
            self.ignored = max(0, self.ignored - 1)
        if tag == self.heading:
            heading = re.sub(r'\s+', ' ', ''.join(self.heading_parts)).strip()
            if heading and not heading.startswith('FilePage'):
                self.headings.append(heading)
            self.heading = None
        if tag in {'p', 'li', 'tr', 'h1', 'h2', 'h3', 'figcaption', 'div', 'section'}:
            self.flush()
        if tag == 'section':
            self.pages.append(Page(f'D1-P{self.page:03}', self.page, self.anchor,
                                   self.headings[0] if self.headings else f'Trang {self.page}', tuple(self.blocks)))
            self.page = None


class Knowledge:
    def __init__(self, path: Path):
        self.path = Path(path)
        content = self.path.read_bytes()
        self.sha256 = sha256(content).hexdigest()
        parser = DeckParser()
        parser.feed(content.decode('utf-8'))
        if [p.file_page for p in parser.pages] != list(range(1, 30)):
            raise ValueError('Nguồn phải chứa đủ 29 trang Day 1, đúng thứ tự, không trùng ID.')
        self.pages = {p.source_id: p for p in parser.pages}
        self.block_map = {b['id']: b['text'] for p in parser.pages for b in p.evidence()['blocks']}
        self.term_sets = {p.source_id: tokens(p.text) for p in parser.pages}

    def page(self, number):
        return self.pages[f'D1-P{number:03}']

    def retrieve(self, query, active_page=None, recent_topic='', limit=4):
        # Current query dominates; history disambiguates short follow-ups only.
        terms = tokens(query)
        if len(terms) <= 2:
            terms |= tokens(recent_topic)
        aliases = {'context': ['ngu canh', 'ban lam viec'], 'token': ['manh chu'],
                   'chatbot': ['llm'], 'temperature': ['nhiet do'], 'agent': ['cong cu']}
        for term, variants in aliases.items():
            if term in terms:
                for variant in variants:
                    terms |= tokens(variant)
        def score(page):
            title = tokens(page.title)
            return sum((3 if t in title else 1) * math.log(1 + 29 / (1 + sum(t in ts for ts in self.term_sets.values())))
                       for t in terms & self.term_sets[page.source_id])
        ranked = sorted(self.pages.values(), key=lambda p: (-score(p), p.file_page))
        chosen = [self.page(active_page)] if active_page is not None else []
        for p in ranked:
            if p not in chosen and score(p) > 0:
                chosen.append(p)
            if len(chosen) >= limit:
                break
        return chosen

    def manifest(self):
        return {'source_path': 'data/d1-slide-hackathon.html', 'sha256': self.sha256,
                'pages': [{k: v for k, v in asdict(p).items() if k != 'blocks'} | {'block_count': len(p.blocks)}
                          for p in self.pages.values()]}
