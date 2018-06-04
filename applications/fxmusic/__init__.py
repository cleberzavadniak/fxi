import subprocess
from urllib.parse import quote_plus as url_quote

from fxi.apps.base import AppBase

import requests
from bs4 import BeautifulSoup


class Entry:
    def __init__(self, title, url, thumbnail_url=None):
        self.title = title
        self.url = url
        self.thumbnail_url = thumbnail_url


class App(AppBase):
    title = 'Music'

    def init(self):
        self.entries = {}
        self.darklyrics_base_url = 'http://www.darklyrics.com'

    def ytsearch(self, term, max_entries=12):
        term = term.replace(' ', '+')  # TODO: proper urlencode, here.
        url = f'https://www.youtube.com/results?search_query={term}'
        response = requests.get(url, headers={'Referer': 'www.youtube.com'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content)

        ol = soup.find('ol', class_='item-section')

        last_thumb_url = None
        entries = tuple(e for e in ol.children if e.name == 'li')[0:max_entries]
        for list_item in entries:
            for img in list_item.find_all('img'):
                src = img.attrs['src']
                if '.jpg' in src and src != last_thumb_url:
                    thumbnail_src = src
                    last_thumb_url = src
                    break

            h3 = list_item.find('h3')
            title_anchor = h3.find('a')
            href = title_anchor.attrs.get('href', None)
            if not href or '/watch' not in href:
                continue

            url = f'https://www.youtube.com{href}'
            title = title_anchor.attrs['title']

            e = Entry(title, url, thumbnail_src)
            video_time_span = list_item.find('span', class_='video-time')
            if video_time_span:
                video_time = video_time_span.text
                e.duration = video_time
            yield e

    def cmd__s(self, *words):
        term = ' '.join(words)

        self.info(f'Searching for {term}...')
        entries = self.ytsearch(term)
        self.info()

        monitor = self.open_monitor(f'Search: {term}')

        self.entries = {}
        index = 0
        for entry in entries:
            monitor.h2(f'{index}: {entry.title}')
            monitor.write(entry.url)
            duration = getattr(entry, 'duration', None)
            if duration:
                monitor.write(f'Duration: {duration}')
            monitor.write_image_from_url(entry.thumbnail_url)
            monitor.hr()

            self.entries[index] = entry
            index += 1

    def cmd__play(self, index):
        entry = self.entries[int(index)]
        self.info('Extracting metadata')
        status, output = subprocess.getstatusoutput(f'youtube-dl -g "{entry.url}"')
        video_url, audio_url = output.split('\n')

        self.current_monitor.clipboard_clear()
        self.current_monitor.clipboard_append(f'mplayer "{audio_url}"')
        self.info('mplayer command copied to clipboard')

        monitor = self.open_monitor(f'Play: {entry.title}')
        response = requests.get(entry.url, headers={'Referer': 'www.youtube.com'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content)

        monitor.h1('Related videos')
        for list_item in soup.find_all('li', class_='related-list-item')[0:20]:
            content = list_item.find('div', class_='content-wrapper')
            if not content:
                continue
            anchor = content.find('a')
            title = anchor.attrs['title']
            href = anchor.attrs['href']
            url = f'https://www.youtube.com{href}'

            thumb_wrapper = list_item.find('div', class_='thumb-wrapper')
            img = thumb_wrapper.find('img')
            thumbnail_src = img.attrs['data-thumb']

            monitor.h2(title)
            monitor.write(url)
            monitor.write_image_from_url(thumbnail_src)

    def cmd__l(self, *words):
        term = ' '.join(words)

        try:
            index = int(term)
        except ValueError:
            return self.find_lyrics(term)

        return self.navigate(index)

    def find_lyrics(self, title):
        return self.find_lyrics_darklyrics(title)

    def find_lyrics_darklyrics(self, title):
        quoted_term = url_quote(title)
        search_url = f'{self.darklyrics_base_url}/search?q={quoted_term}'

        self.info(f'Searching for {title}...')
        response = requests.get(search_url)
        response.raise_for_status()
        self.info()

        soup = BeautifulSoup(response.content)

        monitor = self.open_monitor(title)
        self.entries = {}
        for index, entry in enumerate(soup.find_all('div', class_='sen')):
            anchor = entry.find('a')
            if anchor is None:
                continue

            text = anchor.text
            href = anchor.attrs.get('href', None)

            if href is None:
                continue

            monitor.write(f'{index:>3}: {text}')
            self.entries[index] = (text, self.darklyrics_base_url, href)

    def navigate(self, index):
        text, base_url, url = self.entries[index]
        self.info(f'Loading "{text}"...')

        if url.startswith('../'):
            url = url.strip('../')

        if base_url not in url:
            url = f'{base_url}/{url}'

        response = requests.get(url)
        response.raise_for_status()
        self.info()

        soup = BeautifulSoup(response.content)
        monitor = self.open_monitor(text)

        if '/lyrics/' in url:
            viewer = self.view_lyrics
        else:
            viewer = self.view_band

        return viewer(text, url, monitor, soup)

    def view_band(self, text, url, monitor, soup):
        index = 0
        self.entries = {}

        for album in soup.find_all('div', class_='album'):
            h2 = album.find('h2')
            monitor.h2(h2.text)
            for anchor in album.find_all('a'):
                text = anchor.text
                href = anchor.attrs.get('href', None)

                if href is None:
                    continue

                monitor.write(f'{index:>4}: {text}')

                self.entries[index] = (text, self.darklyrics_base_url, href)
                index += 1
            monitor.hr()

    def view_lyrics(self, text, url, monitor, soup):
        lyrics = soup.find('div', class_='lyrics')

        for element in lyrics.children:
            if element.name == 'h3':
                anchor = element.find('a')
                monitor.hr()
                monitor.h2(anchor.text)
            elif element.name is None:
                monitor.write(element.strip('\n'))
