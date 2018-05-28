import re

import duckduckpy

from fxi.apps.base import AppBase


class App(AppBase):
    title = 'DuckDuckGo'

    def init(self):
        pass

    def show_cover(self, slot, url):
        slot.write_image_from_url(url)

    def cmd__s(self, *words):
        self.info('Searching...')
        term = ' '.join(words)
        q = duckduckpy.query(term)
        self.info()

        monitor = self.open_monitor(f'Search: {term}')

        image = getattr(q, 'image', None)
        if image:
            slot = monitor.add_slot()
            self.enqueue(self.show_cover, slot, image)

        heading = getattr(q, 'heading', None)
        if heading:
            monitor.h1(f'{heading}')

        abstract = getattr(q, 'abstract', None)
        if abstract:
            abstract = re.sub(r'</p>', '\n', abstract)
            abstract = re.sub(r'<br ?/?>', '\n', abstract)
            abstract = re.sub(r'<[^>]+>', ' ', abstract)
            monitor.write(f'{abstract}')

        abstract_url = getattr(q, 'abstract_url', None)
        if abstract_url:
            monitor.write(f'{abstract_url}')
            monitor.clipboard_clear()
            monitor.clipboard_append(f'{abstract_url}')
            self.info(f'Copied to clipboard: {abstract_url}')

        if q.results:
            monitor.h2('Results')
            for result in q.results:
                monitor.write(f'{result.result}')

        if q.related_topics:
            monitor.h2('Related topics')
            for topic in q.related_topics:
                text = getattr(topic, 'text', None)
                name = getattr(topic, 'name', None)

                if text and name:
                    monitor.write(f'{topic.name}: {text}')
                elif text:
                    monitor.write(f'{topic.text}')
                elif name:
                    monitor.write(f'{topic.name}')
                else:
                    monitor.write(f'{topic}')
                monitor.write(f'{topic}')
                monitor.write('-' * 50)

        monitor.hr()
        monitor.write(f'{q}')

        return q
