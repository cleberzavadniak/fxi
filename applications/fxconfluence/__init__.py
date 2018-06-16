from collections import defaultdict

from confluence import Api

from fxi.apps import AppBase
from .parser import Parser


class App(AppBase):
    title = 'Confluence'

    def init(self):
        self.current_page = None
        self.current_space = None
        self.spaces = {}
        self.pages_tree = {}
        self.pages = {}
        self.entries = []

        self.connect()
        self.load_spaces()

    def connect(self):
        url = self.get_config_or_ask('url', label='URL (usually ends in "/wiki")')
        username = self.get_config_or_ask('username', label='Username (usually without the @domain part)')
        password = self.get_config_or_ask('password', label=f"Password for {username} (won't be displayed)", hidden=True)
        # password = self.ask(f"Password for {username} (won't be displayed)", hidden=True)

        with self.info('Conecting...'):
            try:
                self.api = Api(url, username, password)
            except Exception as ex:
                the_type = type(ex)
                self.info(f'{the_type}: {ex}')
                return
            else:
                self.persist_unsaved_config()

    def load_spaces(self):
        with self.info('Loading spaces list'):
            for entry in self.api.listspaces():
                name = entry['name']
                key = entry['key']
                status = entry['status']

                if status == 'CURRENT':
                    try:
                        pages_tree = self.load_pages(key)
                    except Exception as ex:
                        print(f' {ex}')
                        del self.pages_tree[key]
                        continue

                    self.spaces[key] = {
                        'key': key,
                        'name': name,
                        'type': entry['type'],
                        'url': entry['url'],
                        'pages': pages_tree,
                    }
            # TODO: persist it somewhere? It doesn't change that much.

    def load_pages(self, space_key):
        tree = self.pages_tree[space_key] = defaultdict(list)
        for page, _ in self.api.listpages(space_key):
            parent_id = page['parentId']
            tree[parent_id].append(page)

            self.pages[page['id']] = page

        return tree

    def cmd__l(self):
        monitor = self.open_monitor('Spaces')
        for space in self.spaces.values():
            num_pages = len(space["pages"])
            line = f'{space["key"]:>10}: {space["name"]:>30} ({num_pages} pages)'
            monitor.write(line)

    def cmd__v(self, key, debug=False):
        """
        View page.

        Usage: v <space_key> <page title>

        For now, you must write down the entire
        page title. Case sensitive. This surely
        will change in the future.
        """

        debug = bool(debug)

        if key in self.spaces:
            space = self.spaces[key]
            self.current_space = key
            pages_tree = space['pages']
            page = pages_tree['0'][0]
        else:
            space = self.spaces[self.current_space]
            index = int(key)
            pages_tree = space['pages']
            page = self.entries[index]

        page_id = page['id']
        children = pages_tree.get(page_id, None)

        monitor = self.open_monitor(page['title'])
        self.entries = []

        parent_id = page['parentId']

        index = 0
        if parent_id != '0':
            parent = self.pages[parent_id]
            self.entries.append(parent)
            monitor.write(f'{index:>4}: {parent["title"]} (parent)')
            monitor.hr()
            index += 1

        if children:
            monitor.h2('Children pages')
            for index, child in enumerate(children, index):
                monitor.write(f'{index:>4}: {child["title"]}')
                self.entries.append(child)
        else:
            monitor.write('No children pages.')

        monitor.hr()
        self.enqueue(self.load_page, page, monitor, debug)

    def load_page(self, page, monitor, debug=False):
        content_page = self.api.getpage(page['title'], self.current_space)
        content = content_page['content']

        monitor.h1(page['title'])
        parser = Parser(monitor)
        parser.debug = debug
        parser.feed(content)
