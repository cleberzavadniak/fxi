from html.parser import HTMLParser
import re

from fxi.table import Table
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
        self.format_stack = deque([DEFAULT_FMT])
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
        if method is not None:
            fmt = method()
        else:
            fmt = self.format_stack[-1]

        self.format_stack.append(fmt)

    def handle_endtag(self, tag):
        method_name = self.get_method_name('end_tag', tag)
        if self.debug:
            self.monitor.write_fixed(f'{method_name}')

        method = getattr(self, method_name, None)
        if method is not None:
            method()
        self.format_stack.pop()

    def handle_data(self, data):
        fmt = self.format_stack[-1]

        if self.debug:
            self.monitor.write_fixed(f'DATA: {data}')

        if fmt is None:
            return

        if isinstance(fmt, (tuple, list)):
            self.monitor.write_string(data, font=fmt)
            return

        if getattr(fmt, '__call__', None) is not None:
            fmt(data)


class Parser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collections = deque()

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

    def start_tag__ac__plain_text_body(self):
        return DEFAULT_FMT

    def end_tag__ac__plain_text_body(self):
        return CLEAR

    def end_tag__ac__layout_section(self):
        self.monitor.hr()

    def start_tag__table(self):
        self.collections.append([])

    def end_tag__table(self):
        table = self.collections.pop()
        headers = []
        rows = []

        for tr in table:
            row = []
            for cell_type, *cells in tr:
                if cell_type == 'header':
                    headers.append(' '.join(cells))
                else:
                    row.append(' '.join(cells))

            if row:
                rows.append(row)

        slot = self.monitor.add_slot()
        indexes = [[x] for x in range(0, len(headers))]

        widget = Table(slot, indexes, headers)
        widget.render(rows)

    def start_tag__tr(self):
        current_collection = self.collections[-1]
        current_collection.append([])

    def end_tag__tr(self):
        pass

    def start_tag__th(self):
        # table -> tr
        current_collection = self.collections[-1][-1]
        current_collection.append(['header'])
        return self.collect_th_data

    def end_tag__th(self):
        pass

    def collect_th_data(self, data):
        # table -> tr -> th
        th = self.collections[-1][-1][-1]
        th.append(data)

    def start_tag__td(self):
        current_collection = self.collections[-1][-1]
        current_collection.append(['row'])
        return self.collect_td_data

    def collect_td_data(self, data):
        # table -> tr -> td
        current_collection = self.collections[-1][-1][-1]
        current_collection.append(data)
