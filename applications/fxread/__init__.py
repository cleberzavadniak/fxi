from math import ceil

from fxi.apps.base import AppBase

from bs4 import BeautifulSoup
import newspaper


class App(AppBase):
    title = 'Reader'

    def init(self):
        self.page_size = 550
        self.current_page = 0
        self.current_content = None
        self.current_title = None
        self.current_page_counter = 0

    @staticmethod
    def fix_html_pre(soup):
        for pre_element in soup.find_all('pre'):
            for child_element in pre_element.children:
                content = child_element.string
                if content and content.endswith('\n'):
                    child_element.insert_after(soup.new_tag('br'))
                    child_element.string.replace_with(child_element.string.replace('\n', ''))

    def cmd__r(self, url):
        self.info(f'Downloading {url}')
        a = newspaper.Article(url)
        a.download()

        soup = BeautifulSoup(a.html)
        self.fix_html_pre(soup)
        a.html = str(soup)

        self.info(f'Parsing...')
        a.parse()
        self.info()

        self.current_title = a.title
        monitor = self.open_monitor(f'{a.title}')

        if a.authors:
            authors = ', '.join(a.authors)
            monitor.write(f'Authors: {authors}')

        self.current_content = a.text.split('\n')
        self.current_page = 1
        self.current_page_counter = ceil(len(self.current_content) / self.page_size)
        self.view_page()

    def view_page(self):
        page_index = self.current_page - 1
        start = page_index * self.page_size
        end = (start + self.page_size) + 50

        self.enqueue(self.current_monitor.clear)
        self.current_monitor.h2(f'Page {self.current_page} of {self.current_page_counter}')

        for line in self.current_content[start:end]:
            self.current_monitor.write(line)

    def cmd__p(self, page_number):
        page_number = int(page_number) or 1
        if page_number > self.current_page_counter:
            page_number = self.current_page_counter
        self.current_page = page_number
        self.view_page()
