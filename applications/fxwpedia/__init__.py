from fxi.apps.base import AppBase

import wikipedia


class App(AppBase):
    title = 'Wikipedia'

    def init(self):
        self.api = wikipedia
        self.api.set_user_agent('fxi')

    def show_cover(self, slot, url):
        slot.write_image_from_url(url)

    def get_page(self, title):
        self.info(f'Loading {title}')
        return self.api.page(title)

    def show_page(self, monitor, page):
        if not monitor.alive or not self.alive:
            return

        monitor.h2(page.title)

        if page.images:
            slot = monitor.add_slot()
            self.enqueue(self.show_cover, slot, page.images[0])

        monitor.write(page.summary)
        monitor.hr()

    def cmd__s(self, *words):
        """
        Search for <term>

        Usage: s <term>
        """

        term = ' '.join(words)

        self.info('Searching...')
        monitor = self.open_monitor(f'Search: {term}')

        titles = self.api.search(term, results=7)

        for title in titles:
            if not monitor.alive or not self.alive:
                return

            try:
                page = self.get_page(title)
            except wikipedia.exceptions.DisambiguationError as ex:
                continue

                """
                for title in ex.options:
                    try:
                        page = self.get_page(title)
                    except wikipedia.exceptions.DisambiguationError as ex:
                        continue
                    else:
                        self.show_page(monitor, page)
                """
            else:
                self.show_page(monitor, page)

        self.info()

    def cmd__lang(self, language):
        """
        Set language to <language>

        Usage: lang <language>

        You should always use two letters for language, like
        "en", "es" or "pt".
        """

        self.api.set_lang(language)
        self.info(f'Language set to {language}')
