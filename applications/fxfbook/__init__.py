import facepy

from fxi.apps import AppBase
from fxi.table import Table


class MyTable(Table):
    def refresh(self):
        pass


class App(AppBase):
    title = 'DuckDuckGo'

    def init(self):
        self.info('Connecting to Facebook API')
        while True:
            token = self.get_config_or_ask('token', label='Your Graph API token')
            self.api = facepy.GraphAPI(token)
            try:
                self.posts = self.api.get('me/posts')
            except facepy.exceptions.OAuthError as ex:
                self.info(f'OAuthError: {ex}')

                if 'token' in self.config:
                    del self.config['token']
                continue
            self.persist_unsaved_config()
            break
        self.main_list = MyTable(
            self,
            (('message',), ('id',)),
            ('Messages', 'ID')
        )
        self.info()

    def render(self):
        self.main_list.render(self.posts['data'])

    def cmd__post(self, *words):
        content = ' '.join(words)
        self.info('Sending...')
        self.api.post('me/feed', message=content)
        self.info('Status update sent')

    def cmd__ls(self):
        posts = self.api.get('me/posts')
        monitor = self.open_monitor('Posts')
        for post in posts['data']:
            monitor.write(f'{post}')

    def cmd__del(self, post_id):
        self.info('Deleting...')
        response = self.api.delete(post_id)
        monitor = self.open_monitor('Deletion')
        monitor.write(f'{response}')
        self.info('Deleted.')
