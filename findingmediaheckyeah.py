import requests
import random
from itertools import chain
import os
import string
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")


# API CALLING FUNCTIONS

def _search_for_movie(keywords, page=1) -> dict:
    url = "https://api.themoviedb.org/3/search/movie"

    parameters = {
        "api_key": api_key,
        "query": keywords,
        "page": page
    } 
    response = requests.get(url, params=parameters)

    return response.json()

def _search_for_show(keywords, page=1) -> dict:
    url = "https://api.themoviedb.org/3/search/tv"
    parameters = {
        "api_key": api_key,
        "query": keywords,
        "page": page
    } 
    response = requests.get(url, params=parameters)
    return response.json()

def _get_genres_for_movies() -> dict:
    url = "https://api.themoviedb.org/3/genre/movie/list"
    parameters = {
        "api_key": api_key,
        
    }
    response = requests.get(url, params=parameters)
    return response.json()

def _get_genres_for_tv() -> dict:
    url = "https://api.themoviedb.org/3/genre/tv/list"
    parameters = {
        "api_key": api_key,

    }
    response = requests.get(url, params=parameters)
    return response.json()

def get_media_from_id(media_id: int, type_of_media: str):
    """
    Docstring for get_media_from_id
    
    :param media_id: The id of the media
    :param type_of_media: Description
    :return: Dictionary containing media metadata
    """

    url = f'https://api.themoviedb.org/3/{type_of_media}/{media_id}?api_key={api_key}&external_source=imdb_id'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:  # Return the response if the id belongs to a movie.
        return response.json()
    
    url = f'https://api.themoviedb.org/3/tv/{media_id}?api_key={api_key}&external_source=imdb_id'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    
    return response.json()

def discover_movies(page_number: int = 1) -> dict:
    """
    Return a dictionary of movies
    
    :param page_number: Page number parameter for the API
    :return: A dictionary, with a "result" key filled with dictionaries 
    with the metadata of the movie. 
    """
    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": api_key,
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": page_number,
        "sort_by": "popularity.desc"
    }

    response = requests.get(url, params=params)
    
    return response

def discover_shows(page_number: int = 1):
    """
    Return a dictionary of movies
    
    :param page_number: Page number parameter for the API
    :return: A dictionary, with a "result" key filled with dictionaries 
    with the metadata of the show. 
    """
    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": api_key,
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": page_number,
        "sort_by": "popularity.desc"
    }

    response = requests.get(url, params=params)
    
    return response

# MEDIA RECOMMENDER / FINDER CLASS

class MediaRecommender:
    def __init__(self):
        """Initialize a MediaRecommender instance"""
        self._genre_cache = None
        self.model = NearestNeighbors(metric='cosine')

    def _get_all_genres(self):
        if self._genre_cache is None:
            movies_genres = _get_genres_for_movies().get('genres', [])
            tv_genres = _get_genres_for_tv().get('genres', [])
            
            self._genre_cache = {}
            for genre in chain(movies_genres, tv_genres):
                self._genre_cache[genre['id']] = genre['name']
        return self._genre_cache
    
    def get_genre_from_id(self, genre_id: int) -> str:
        """
        Returns the genre based on the id

        :param genre_id: Description
        :return: Description
        """
        try:
            genres_map = self._get_all_genres()
            return genres_map.get(genre_id, None)
        except:
            return None

    # TODO: Remove this method once recommender is fully implemented.     
    def get_random_movie(self):
        chosen_movie = None
        while chosen_movie == None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(_search_for_movie(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            movies_in_chosen_page = _search_for_movie(random_letter, page=chosen_page)
            for movie_info in movies_in_chosen_page['results']:
                try:
                    if  len(movie_info['genre_ids']) and movie_info['popularity'] >= 20 and movie_info['vote_average'] >= 6:
                        chosen_movie = movie_info
                except:
                    pass
                    
        return chosen_movie
    
    # TODO: Remove this method once recommender is fully implemented.
    def get_random_show(self):
        chosen_tv = None
        while chosen_tv == None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(_search_for_show(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            show_in_chosen_page = _search_for_show(random_letter, page=chosen_page)
            
            for show_info in show_in_chosen_page['results']:
                try:
                    if len(show_info['genre_ids']) and show_info['popularity'] >= 20 and show_info['vote_average'] >= 6:
                        chosen_tv = show_info
                except:
                    pass

        return chosen_tv
        
    def get_media_from_query(self, query: str, page_num: int, search_filter: int ='popularity') -> list:
        """
        Get a list of media to appear on page.
        
        :param query: The query used to search for media.
        :param page_num: The page number the user is currently on.
        :param _filter: The type of filter used to filter the results.
        :return: A list with the media that will appear on the page.
        """

        PER_PAGE = 5
        
        combined = []
        api_page = 1

        # Fetch pages until we have enough items for this page.
        with ThreadPoolExecutor(max_workers=2) as executor:
            while len(combined) < page_num * PER_PAGE:
                
                # Concurrently call apis.

                movie_future = executor.submit(_search_for_movie, query, api_page)
                show_future = executor.submit(_search_for_show, query, api_page)

                movie_page = movie_future.result().get('results', [])
                show_page = show_future.result().get('results', [])
            
                if not movie_page and not show_page:
                    break
                
                for m in movie_page:
                    m['_type'] = 'movie'
                    combined.append(m)

                for s in show_page:
                    s['_type'] = 'show'
                    combined.append(s)

                api_page += 1

        
        combined.sort(key=lambda x: float(x.get(search_filter, 0)), reverse=True)

        # Slice exactly the items for this app page.

        start = (page_num - 1) * PER_PAGE
        end = start + PER_PAGE
        page_slice = combined[start:end]

        media_on_page = [
            self.format_media_dict(item, item['_type'])
            for item in page_slice
        ]

        return media_on_page

    
    def format_media_dict(self, data: dict, type_of_media: str):
        """
        Simplfies a dictionary of media.

        :param data: The dictionary of the media.
        :param type_of_media: The type of the media (movie or show).
        :return: The formatted, processed media dict.
        """

        try:
            title = f"{data['original_title']}" 
        except:           
            title = f"{data['name']}" 
         
        try:
            release_date = data['release_date']
        except:
            release_date = data['first_air_date']

        try:
            return {
                'title': title,
                'overview': data['overview'],
                'rating': f"{data['vote_average']}/10",
                'genres': [self.get_genre_from_id(genre) for genre in data['genre_ids']],
                'release date': release_date,
                'id': data['id'],
                'poster_path': data['poster_path'],
                'type of media': type_of_media
                }
        except:
            return {
                    'title': title,
                    'overview': data['overview'],
                    'rating': f"{data['vote_average']}/10",
                    'genres': [genre['name'] for genre in data['genres']],
                    'release date': release_date,
                    'id': data['id'],
                    'poster_path': data['poster_path'],
                    'type of media': type_of_media
                    }

    def _encode_genres(self, media_dict):
        return [int(gen in media_dict['genres']) for gen in self._genre_cache]

    def vectorize_media_dict(self, media_dict):
        genres = self._encode_genres(media_dict)

        return np.array(
                [  # Items to consider / compare.
            float(media_dict['rating'][:-3]),  # Remove the /10 at the end of the string.
            *genres
                ]
            )
    
    def get_items(self, max_pages=2000):
        for i in range(max_pages):
            pass

    def _format_media_data(self, data: dict):
        try:
            title = f"{data['original_title']}" 
        except:    
            title = f"{data['name']}" 
       
        try:
            release_date = data['release_date']
        except:
            release_date = data['first_air_date']
        
        return f"{title}\n{data['overview']}\nRating: {data['vote_average']}\n{','.join([self.get_genre_from_id(genre) for genre in data['genre_ids']])}\n{release_date[:4]}"
   

