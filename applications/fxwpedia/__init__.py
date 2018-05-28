from fxi.apps.base import AppBase

import wikipedia


class App(AppBase):
    title = 'Wikipedia'

    def init(self):
        self.api = wikipedia
        self.api.set_user_agent('fxi')

    def show_cover(self, slot, url):
        slot.write_image_from_url(url)

    def cmd__s(self, *words):
        term = ' '.join(words)

        self.info('Searching...')
        monitor = self.open_monitor(f'Search: {term}')
        for title in self.api.search(term, results=7):
            if not monitor.alive or not self.alive:
                return

            page = self.api.page(title)

            monitor.h2(page.title)

            if page.images:
                slot = monitor.add_slot()
                self.enqueue(self.show_cover, slot, page.images[0])

            monitor.write(page.summary)
            monitor.hr()
        self.info()

    def cmd__lang(self, language):
        self.api.set_lang(language)
        self.info(f'Language set to {language}')
