import duckduckpy

from fxi.apps.base import AppBase


class App(AppBase):
    title = 'DuckDuckGo'

    def init(self):
        pass

    def cmd__SLASH(self, *words):
        self.info('Searching...')
        term = ' '.join(words)
        q = duckduckpy.query(term)

        monitor = self.open_monitor(f'Search: {term}')

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

        self.info()
