from requests.exceptions import ConnectionError
from translate import Translator

from fxi.apps import AppBase


class App(AppBase):
    title = 'Translate'

    def init(self):
        self.translators = {}
        self.to_lang = None
        self.from_lang = None

    @property
    def key(self):
        return f'{self.from_lang}:{self.to_lang}'

    @property
    def translator(self):
        if self.key not in self.translators:
            self.translators[self.key] = Translator(from_lang=self.from_lang, to_lang=self.to_lang)
        return self.translators[self.key]

    def cmd__set(self, from_lang, to_lang):
        """
        Set "from" and "to" language

        Usage: set <from_lang> <to_lang>

        <from_lang> and <to_lang> should always use two letters,
        like "en", "es" or "pt".
        """
        self.from_lang = from_lang
        self.to_lang = to_lang

        self.info(f'Translator set to {self.from_lang} -> {self.to_lang}')
        self.open_monitor()

    def open_monitor(self):
        super().open_monitor(f'{self.from_lang} -> {self.to_lang}')

    def translate(self, phrase):
        try:
            return self.translator.translate(phrase)
        except ConnectionError:
            del self.translators[self.key]
            return self.translator.translate(phrase)

    def cmd__t(self, *words):
        """
        Translate a <phrase> accodingly to <from_lang> and <to_lang>
        previously set with "set" command

        Usage: t <phrase>
        """

        if not self.from_lang or not self.to_lang:
            self.info('Use the command "set <from> <to>", before.')
            return

        self.info('Translating...')
        if words:
            phrase = ' '.join(words)

        translation = self.translate(phrase)
        self.current_monitor.hr()
        self.current_monitor.write('->')
        self.current_monitor.write(translation)
        self.info()
