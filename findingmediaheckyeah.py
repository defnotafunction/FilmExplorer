import requests
from bs4 import BeautifulSoup
import random
from itertools import chain
import csv
import json
import datetime
import os
import string
def fun_game():
    response = requests.get("https://opentdb.com/api.php?amount=50&category=18&difficulty=medium&type=multiple").json()
    while True:
        question = random.choice(response['results'])
        print(question['question'])
        answers = list(chain(question['incorrect_answers'], [question['correct_answer']]))
        random.shuffle(answers)
        print('\n'.join([f"{idx+1} - {choice}" for idx, choice in enumerate(answers)]))
        user_answer = int(input('Answer Question: '))
        print(f"{'Correct!' if answers[user_answer-1] == question['correct_answer'] else f'Wrong, the answer was ' + question['correct_answer']}!")

api_key = "b17b5fc6d4925775f336ee364676badd"
def search_for_movie(keywords, page=1) -> dict:
    url = "https://api.themoviedb.org/3/search/movie"

    parameters = {
        "api_key": api_key,
        "query": keywords,
        "page": page
    } 
    response = requests.get(url, params=parameters)

    return response.json()
def search_for_show(keywords, page=1) -> dict:
    url = "https://api.themoviedb.org/3/search/tv"
    parameters = {
        "api_key": api_key,
        "query": keywords,
        "page": page
    } 
    response = requests.get(url, params=parameters)
    return response.json()
def get_genres_for_movies() -> dict:
    url = "https://api.themoviedb.org/3/genre/movie/list"
    parameters = {
        "api_key": api_key,
        
    }
    response = requests.get(url, params=parameters)
    return response.json()
def get_genres_for_tv() -> dict:
    url = "https://api.themoviedb.org/3/genre/tv/list"
    parameters = {
        "api_key": api_key,

    }
    response = requests.get(url, params=parameters)
    return response.json()
def get_media_from_id(id, type_of_media):
    url = f'https://api.themoviedb.org/3/{type_of_media}/{id}?api_key={api_key}&external_source=imdb_id'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    url = f'https://api.themoviedb.org/3/tv/{id}?api_key={api_key}&external_source=imdb_id'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    return response.json()
            
class MediaRecommender:
    def load_media_viewed(self) -> list:
        try:
            with open(os.path.join('userdata', 'mediaviewed.csv')) as mediafile:
                rows = csv.reader(mediafile)
                return list(rows)
        except FileNotFoundError:
            self.create_media_viewed()
            
    def save_media_viewed(self) -> None:
        with open(os.path.join('userdata', 'mediaviewed.csv'), 'w') as mediafile:
            csv_writer = csv.writer(mediafile)
            for row in self.media_viewed:
                csv_writer.writerow(row)
                
    def create_media_viewed(self) -> None:
        with open(os.path.join('userdata', 'mediaviewed.csv'), 'w') as mediafile:
            csv_writer = csv.writer(mediafile)
            csv_writer.writerow(['title','user_rating','public_rating','genre1','genre2','genre3', 'date_finished'])
            
    def get_genre_from_id(self, genre_id: int) -> list:
        try:
            return [id_dictionary['name'] for id_dictionary in chain(get_genres_for_movies()['genres'], get_genres_for_tv()['genres']) if genre_id == id_dictionary['id']][0]
        except:
            return None
            
    def create_user_liked_genres_file(self):
        with open(os.path.join('userdata', 'user_liked_genres.json'), 'w') as genres:
            json.dump({info['name']: random.random() for genre in chain(get_genres_for_movies().values(), get_genres_for_tv().values()) for info in genre }, genres, indent=4)
            
    def load_user_liked_genres_file(self):
        try:
            with open(os.path.join('userdata', 'user_liked_genres.json'), 'r') as genres:
                return json.load(genres)
        except FileNotFoundError:
            self.create_user_liked_genres_file()
            
    def save_user_liked_genres_file(self):
        with open(os.path.join('userdata', 'user_liked_genres.json'), 'w') as genres:
            json.dump(self.user_genre_ratings, genres, indent=4)
            
    def decrease_all_genre_weights(self, *exceptions, rate=0.01):
        for genre, weight in self.user_genre_ratings.items():
            if genre not in exceptions:
                self.user_genre_ratings[genre] -= random.random()*rate
                
    def increase_genre_weights(self, *genres, rate=0.1):
        for genre in genres:
            self.user_genre_ratings[genre] += random.random()*rate
    
    def change_based_user_review(self, media_info:dict, user_rating: float, enjoyable: bool):
        genre1 = media_info['genre_ids'][0]
        try:
            genre2 = media_info['genre_ids'][1]
        except:
            genre2 = None
        try:
            genre3 = media_info['genre_ids'][2] 
        except:
            genre = None
        self.media_viewed.append([media_info['title'], user_rating, media_info['vote_average'], genre1,genre2,genre3, datetime.datetime.today().strftime('MONTH-%m DAY-%d, YEAR-%Y')])
        self.increase_genre_weights(media_info['genre_ids'][0], media_info['genre_ids'][1], media_info['genre_ids'][2])
        
    def sort_genres_by_likeability(self):
        return [genre for genre in reversed(sorted(self.user_genre_ratings, key=lambda x: self.user_genre_ratings[x]))]
        
    def get_random_movie_from_genres(self, genres:list):
        chosen_movie = None
        while chosen_movie is None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(search_for_movie(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            movies_in_chosen_page = search_for_movie(random_letter, page=chosen_page)
            for movie_info in movies_in_chosen_page['results']:
                try:
                    if all(self.get_genre_from_id(genre_id) in genres for genre_id in movie_info['genre_ids']) and len(movie_info['genre_ids']) and movie_info['popularity'] >= 20 and movie_info['vote_average'] >= 6:
                        chosen_movie = movie_info
                except:
                    pass
                    
        return chosen_movie
    
    def get_random_movie(self):
        chosen_movie = None
        while chosen_movie == None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(search_for_movie(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            movies_in_chosen_page = search_for_movie(random_letter, page=chosen_page)
            for movie_info in movies_in_chosen_page['results']:
                try:
                    if  len(movie_info['genre_ids']) and movie_info['popularity'] >= 20 and movie_info['vote_average'] >= 6:
                        chosen_movie = movie_info
                except:
                    pass
                    
        return chosen_movie
    
    def get_random_show(self):
        chosen_tv = None
        while chosen_tv == None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(search_for_show(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            show_in_chosen_page = search_for_show(random_letter, page=chosen_page)
            for show_info in show_in_chosen_page['results']:
                try:
                    if len(show_info['genre_ids']) and show_info['popularity'] >= 20 and show_info['vote_average'] >= 6:
                        chosen_tv = show_info
                except:
                    pass
        return chosen_tv
        
    def get_random_show_from_genres(self, genres:list):
        chosen_tv = None
        while chosen_tv == None:
            random_letter = random.choice(string.ascii_lowercase)
            total_pages = int(search_for_show(random_letter)['total_pages'])
            chosen_page = random.randint(1, total_pages)
            show_in_chosen_page = search_for_show(random_letter, page=chosen_page)
            for show_info in show_in_chosen_page:
                try:
                    if all(self.get_genre_from_id(genre_id) in genres for genre_id in show_info['genre_ids']) and len(show_info['genre_ids']) and show_info['popularity'] >= 20 and show_info['vote_average'] >= 6:
                        chosen_tv = show_info
                except:
                    pass
        return chosen_tv
    
    def recommend_media(self, specific=False):
        if specific:
            most_liked_genres = self.sort_genres_by_likeability()[:3]
        else:
            most_liked_genres = self.sort_genres_by_likeability()[random.randint(0,3)]
        recommended_media = [self.get_random_movie_from_genres(most_liked_genres) if random.randint(1,2) == 1 else self.get_random_show_from_genres(most_liked_genres) for i in range(3) ]
        return recommended_media
    
    def format_media_dict(self, data, type_of_media):
        try:
            title = f"{data['original_title']}" 
        except:    
            
            title = f"{data['name']}" 
       
            
        try:
            release_date = data['release_date']
        except:
            release_date = data['first_air_date']
        try:
            return {'title': title, 'overview': data['overview'], 'rating': data['vote_average'], 'genres': [self.get_genre_from_id(genre) for genre in data['genre_ids']], 'release date': release_date, 'id': data['id'], 'poster_path': data['poster_path'], 'type_of_media': type_of_media}
        except:
            return {'title': title, 'overview': data['overview'], 'rating': data['vote_average'], 'genres': [genre['name'] for genre in data['genres']], 'release date': release_date, 'id': data['id'], 'poster_path': data['poster_path'], 'type_of_media': type_of_media}
        


    def format_media_data(self, data):
        try:
            title = f"{data['original_title']}" 
        except:    
            
            title = f"{data['name']}" 
       
            
        try:
            release_date = data['release_date']
        except:
            release_date = data['first_air_date']
        
        return f"{title}\n{data['overview']}\nRating: {data['vote_average']}\n{','.join([self.get_genre_from_id(genre) for genre in data['genre_ids']])}\n{release_date[:4]}"
   

