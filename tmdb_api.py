import requests
from itertools import chain
import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

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

def _get_all_languages():
    url = f"https://api.themoviedb.org/3/configuration/languages?api_key={api_key}"
    response = requests.get(url)
    return response.json()

def check_if_id_movie(media_id: int) -> bool:
    """
    Checks if a media_id belongs to a movie.
    
    :param media_id: The ID of the media.
    :return: True if the media_id belongs to a movie; otherwise, it returns false.
    """
    url = f'https://api.themoviedb.org/3/movie/{media_id}?api_key={api_key}&external_source=imdb_id'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def get_media_from_id(media_id: int, type_of_media: str = 'movie'):
    """
    Get a media dictionary from its ID.
    
    :param media_id: The id of the media.
    :param type_of_media: Type of media ('movie' or 'tv').
    :return: Dictionary containing media metadata.
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
        "sort_by": "popularity.desc",
        "vote_average.gte": 7,
        "vote_count.gte": 500
    }

    response = requests.get(url, params=params)
    
    return response.json()

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
        "sort_by": "popularity.desc",
        "vote_average.gte": 7,
        "vote_count.gte": 500
    }

    response = requests.get(url, params=params)
    
    return response.json()

# MEDIA RECOMMENDER / FINDER CLASS

class MediaRecommender:
    def __init__(self, model_dataset_pages: int = 500):
        """Initialize a MediaRecommender instance"""
        self._genre_cache = self._get_all_genres()
        self._language_cache = _get_all_languages()
        self._model = NearestNeighbors(metric='cosine')
        self.model_data_dir = os.path.join(BASE_DIR, 'cache', "model.npz")
        
        if os.path.exists(self.model_data_dir):
            self._media_vectors, self._media_ids = self._load_media_arrays()
        else:
            self._media_vectors, self._media_ids = self.get_vectorized_media(model_dataset_pages)
        
        self.fit_model()
        self._save_media_arrays()

    def _save_media_arrays(self) -> None:
        np.savez_compressed(self.model_data_dir,
                    vectors=self._media_vectors,
                    ids=np.array(self._media_ids, dtype=np.int64))


    def _load_media_arrays(self) -> tuple[list, list]:
        arrays = np.load(self.model_data_dir)
        vectors = arrays['vectors']
        ids = arrays['ids'].tolist()
        assert len(ids) == vectors.shape[0]
        return vectors, ids

    def _get_all_genres(self):
        if not hasattr(self, '_genre_cache') or self._genre_cache is None:
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

    
    def format_media_dict(self, data: dict, type_of_media: str) -> dict:
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

    def _encode_genres(self, media_dict) -> list:  # One hot encoding
        if 'genres' in media_dict:
            genres_to_check = [genre['id'] for genre in media_dict['genres']]
        else:
            genres_to_check = media_dict['genre_ids']

        return [int(gen in genres_to_check) for gen in self._genre_cache]

    def _encode_languages(self, media_dict):  # One hot encoding
        return [int(media_dict["original_language"] == lang["iso_639_1"]) for lang in self._language_cache]

    # TMDB isn't specific with its genres (no anime genre).
    # So, I added other features such as language and whether it's an adult film
    def vectorize_media_dict(self, media_dict) -> np.array:
        genres = self._encode_genres(media_dict)
        language = self._encode_languages(media_dict)

        return np.array(
                [  # Features to weigh in and compare.  
            *genres,
            *language,
            int(media_dict['adult'])
                ]
            )
    
    def _get_media(self, max_pages: int) -> list[dict]:
        media = []
        for i in range(max_pages):
            discovered_mov  = discover_movies(page_number=i+1)
            discovered_shows = discover_shows(page_number=i+1)

            for mov in discovered_mov['results']:
                media.append(mov)

            for show in discovered_shows['results']:
                media.append(show)

        return media

    def get_vectorized_media(self, max_pages: int) -> tuple[np.array, list]:
        """
        Gets two parallel lists, one array containing the vectors, the second contains the corresponding ID.

        :param max_pages: The maximum amount of pages used in requesting the TMDB's API.
        :return: Returns two parallel lists.
        """
        media_vectors = []
        media_ids = []
        
        for m in self._get_media(max_pages):
            media_vectors.append(self.vectorize_media_dict(m))
            media_ids.append(m['id'])

        return np.array(media_vectors), media_ids

    def fit_model(self) -> None:
        self._model.fit(self._media_vectors)

    def recommend(self, liked_ids: list[int], n_recommendations: int = 5) -> list[int]:
        """
        Returns TMDB IDs of recommended movies based on liked IDs.

        :param liked_ids: List of user's liked media's IDs.
        :param n_recommendations: Number of recommendations to return.
        :return: List of recommended TMDB IDs.
        """
        liked_media = [get_media_from_id(_id) for _id in liked_ids]
        liked_vectors = [self.vectorize_media_dict(m) for m in liked_media]
        liked_vector_mean = np.mean(liked_vectors, axis = 0)

        # Liked movies themselves may appear in the neighbors, so +len(liked_ids).
        distances, indices = self._model.kneighbors([liked_vector_mean], n_neighbors=n_recommendations + len(liked_ids)) 
        all_rec_ids = [self._media_ids[i] for i in indices[0]]
       
        recommended_ids = set([mid for mid in all_rec_ids if mid not in liked_ids])
        recommended_ids = list(recommended_ids)

        return recommended_ids[:n_recommendations]


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
   

