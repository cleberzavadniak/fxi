import random
import time

from fxi.apps import AppBase
from fxi.table import Table


class App(AppBase):
    def init(self):
        self.main_list = Table(
            self,
            (('phrase',), ('count', 'rand'), ('word',)),
            ('Phrase', '', 'Word')
        )

        self.data = []
        self.load_fake_data()

    def load_fake_data(self):
        with open(__file__) as file_object:
            words = tuple(set(file_object.read().replace('\n', '').split(' ')))

        for row in range(0, 200):
            entry = {}
            num_words = random.randint(1, 5)
            entry['phrase'] = ' '.join(random.sample(words, num_words))
            entry['count'] = num_words
            entry['rand'] = random.randint(0, 100)
            entry['word'] = random.choice(words)
            self.data.append(entry)

    def render(self):
        self.h1('Test App')
        self.main_list.render(self.data)

    # Commands:
    def cmd__sleep(self, *args):
        """
        Sleep for <n> seconds

        Usage: sleep <n>
        """

        t = int(args[0])
        self.info(f'Sleeping for {t} seconds')
        time.sleep(t)
        self.info(f'Waked up!')

    def cmd__monitor(self, *args):
        """
        Tests Monitor class, writing some garbage into it

        Usage: monitor
        """

        monitor = self.open_monitor()
        for i in range(0, 250):
            if not self.alive or not monitor.alive:
                return

            indentation = random.randint(0, 3)
            monitor.write(f'Line {i} (indentation={indentation})', indentation=indentation)
            time.sleep(random.randint(0, 10) / 10)
        monitor.close()

    def cmd__ask(self, *args):
        """
        Tests the "ask" subsystem, displaying it with "info"

        Usage: ask <question>
        """

        question = ' '.join(args)
        self.info(self.fxi.prompt.ask(question))
