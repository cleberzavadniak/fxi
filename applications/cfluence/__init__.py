from collections import defaultdict
from pathlib import Path

from confluence import Api

from fxi.apps.base import AppBase
from fxi.apps.main_list import MainList


class MyMainList(MainList):
    def refresh(self):
        for entry in self.entries:
            entry.mark_as('loading')
            # name = entry.data['name']
            # new_data = self.parent.refresh_queue(name)
            # entry.refresh(new_data)


class App(AppBase):
    title = 'Confluence'

    def init(self):
        self.cwd = Path('/')  # <space-key>/page1/page2
        self.spaces = {}

        username = self.get_config_or_ask('username', label='Username (usually without the @domain part)')
        password = self.get_config_or_ask('password', hidden=True, label="Password (won't be displayed)")
        url = self.get_config_or_ask('url', label='URL (usually ends in "/wiki")')

        try:
            self.api = Api(url, username, password)
        except Exception as ex:
            the_type = type(ex)
            self.info(f'{the_type}: {ex}')
            return
        else:
            self.persist_unsaved_config()

        self.pages = {}
        self.load_spaces()

    def load_spaces(self):
        self.info('Loading spaces list')

        for entry in self.api.listspaces():
            name = entry['name']
            key = entry['key']
            status = entry['status']

            print('Space:', name)

            if status == 'CURRENT':
                try:
                    self.load_pages(key)
                except Exception as ex:
                    print(f' {ex}')
                    del self.pages[key]
                    continue

                self.spaces[name] = {
                    'name': name,
                    'type': entry['type'],
                    'key': entry['key'],
                    'url': entry['url'],
                    'pages': [],
                }
        self.info()
        # TODO: save it somewhere. It doesn't change that much.

    def load_pages(self, space_key):
        tree = self.pages[space_key] = defaultdict(list)
        for page, _ in self.api.listpages(space_key):
            parent_id = page['parentId']
            tree[parent_id].append(page)

    def cmd__ls(self, path=None):
        if path:
            title = f'ls {path}'
        else:
            title = 'ls'
        monitor = self.open_monitor(title)

        path = Path(path or '.')
        target = self.cwd / path

        try:
            space_key = target.parts[1]
        except IndexError:
            space_key = None

        if space_key is None:
            for space in sorted(self.spaces.values(), key=lambda x: x['type'] == 'global', reverse=True):
                if space['type'] == 'global':
                    monitor.write('{s[key]} : {s[name]}'.format(s=space))
                else:
                    monitor.write('{s[key]} : {s[name]} ({s[type]})'.format(s=space))
            return

        path = Path(*(path.parts[1:]))
        basename = path.name

        # TODO: search by title, too.
        page_id = basename or '0'

        for page in self.pages[space_key][page_id]:
            if page['permissions'] == '0':
                monitor.write('{p[id]} : {p[title]}'.format(p=page))
            else:
                monitor.write('{p[id]} : {p[title]} (permissions: {p[permissions]})'.format(p=page))

    def cmd__pdb(self):
        import pdb; pdb.set_trace()
