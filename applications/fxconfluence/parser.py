from html.parser import HTMLParser
import re

from collections import deque


HEADER_FONT = 'Ubuntu'
FONT = 'Terminus'
SIZE = 10
DEFAULT_FMT = (FONT, SIZE)
CLEAR = None


class BaseParser(HTMLParser):
    def __init__(self, monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = monitor
        self.format_stack = deque()
        self.attrs = {}
        self.debug = False

    @staticmethod
    def get_method_name(prefix, tag):
        method_name = f'{prefix}__{tag}'.replace('-', '_')
        return re.sub(r'[^a-zA-Z0-9_]', '__', method_name)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)
        method_name = self.get_method_name('start_tag', tag)
        if self.debug:
            self.monitor.write_fixed(f'{method_name} ({attrs})')

        method = getattr(self, method_name, None)
        if method is None:
            return

        fmt = method()
        self.format_stack.append(fmt)

    def handle_endtag(self, tag):
        method_name = self.get_method_name('endtag', tag)
        if self.debug:
            self.monitor.write_fixed(f'{method_name}')

        method = getattr(self, method_name, None)
        if method is None:
            return

        method()
        self.format_stack.pop()

    def handle_data(self, data):
        fmt = self.format_stack[-1]
        if fmt:
            self.monitor.write_string(data, font=fmt)


class Parser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_tag__p(self):
        return DEFAULT_FMT

    def start_tag__h1(self):
        return (HEADER_FONT, SIZE + 6)

    def start_tag__h2(self):
        return (HEADER_FONT, SIZE + 4)

    def start_tag__h3(self):
        return (HEADER_FONT, SIZE + 4)

    def end_tag__hr(self):
        self.monitor.hr()

    def start_tag__ac__structured_macro(self):
        macro_name = self.attrs.get('ac:name', self.attrs)
        self.monitor.write_fixed(f'MACRO:{macro_name}')

    def end_tag__ac__layout_section(self):
        self.monitor.hr()
