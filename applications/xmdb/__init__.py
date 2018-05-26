from imdb import IMDb

from fxi.apps.base import AppBase


class App(AppBase):
    title = 'IMDb'

    def init(self):
        self.api = IMDb()

    def cmd__s(self, *args):
        term = ' '.join(args)

        self.info('Searching...')
        movies = self.api.search_movie(term)

        monitor = self.open_monitor(f'Search: {term}')

        for movie_info in movies[0:15]:
            title = movie_info.get('title')
            kind = movie_info.get('kind')

            if kind in ('video game', 'episode'):
                continue

            year = movie_info.get('year')
            monitor.write(f'{kind}: {title} ({year})')

            identifier = movie_info.getID()
            self.info(f'Loading: {title} ({identifier})...')

            movie = self.api.get_movie(identifier)
            rating = movie.get('rating')
            votes = movie.get('votes')

            cast = [person.get('name') for person in movie.get('cast', [])[0:7]]

            monitor.write(f'{rating} ({votes} votes)', 1)
            monitor.write(', '.join(cast), 1)
            monitor.hr()
        self.info()
