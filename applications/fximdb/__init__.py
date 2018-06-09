from imdb import IMDb

from fxi.apps.base import AppBase


class App(AppBase):
    title = 'IMDb'

    def init(self):
        self.api = IMDb()

    def download_cover(self, slot, url):
        with self.info(f'Downloading cover from {url}'):
            slot.write_image_from_url(url)

    def download_more_info_about_movie(self, frame_slot, movie_info):
        identifier = movie_info.getID()
        movie = self.api.get_movie(identifier)
        rating = movie.get('rating')
        if rating:
            votes = movie.get('votes')
            frame_slot.write(f'{rating} ({votes} votes)', 1)

        cover_thumbnail_url = movie.get('cover url')
        if cover_thumbnail_url:
            slot = frame_slot.add_slot()
            self.enqueue(self.download_cover, slot, cover_thumbnail_url)

        cast = [person.get('name') for person in movie.get('cast', [])[0:7]]
        frame_slot.write(', '.join(cast), 1)

    def cmd__s(self, *args):
        """
        Search for <term>

        Usage: s <term>
        """

        term = ' '.join(args)

        with self.info('Searching...'):
            movies = self.api.search_movie(term)

        monitor = self.open_monitor(f'Search: {term}')

        for movie_info in movies[0:7]:
            title = movie_info.get('title')
            kind = movie_info.get('kind')

            if kind in ('video game', 'episode'):
                continue

            year = movie_info.get('year')
            monitor.write(f'{kind}: {title} ({year})')

            frame_slot = monitor.add_frame_slot()
            self.enqueue(self.download_more_info_about_movie, frame_slot, movie_info)

            monitor.hr()
