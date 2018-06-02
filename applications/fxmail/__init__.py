from fxi.apps.base import AppBase
from fxi.apps.main_list import MainList

import easyimap


class App(AppBase):
    title = 'E-mail'

    def init(self):
        self.client = None
        self.username = None
        self.messages = {}
        self.main_list = MainList(
            self,
            (('from',), ('subject',), ('date',)),
            ('From', 'Subject', 'When')
        )

        self.info('Open a new mailbox using: open <host> <username>')

    def cmd__open(self, host, username):
        if '.' not in host:
            host = f'imap.{host}.com'

        password = self.ask(f'Password for {username}', hidden=True)
        self.client = easyimap.connect(host, username, password)
        self.info('Client connected')
        self.username = username
        self.enqueue(self.reload)

    def reload(self, max_messages=5):
        self.info('Loading messages...')
        for message in self.client.listup(max_messages):
            self.add_message(message)
        self.info()
        self.main_list.render(self.messages)
        self.enqueue(self.reload_and_refresh)

    def reload_and_refresh(self, max_messages=80):
        self.info('Loading more messages...')
        for message in self.client.listup(max_messages):
            self.add_message(message)
        self.info()
        self.main_list.render(self.messages)

    def add_message(self, message):
        self.messages[message.uid] = {
            'object': message,
            'subject': f'{message.title}'.encode('utf-8'),
            'from': message.from_addr,
            'to': message.to,
            'date': message.date
        }

    def refresh(self):
        self.enqueue(self.reload)
        self.main_list.render(self.messages)

    def render(self):
        self.main_list.render(self.messages)
