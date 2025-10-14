from flask import *
app = Flask(__name__)
from findingmediaheckyeah import MediaRecommender
recommender = MediaRecommender()
all_movie_genres = ['Action', 'Abenteuer', 'Animation', 'Komödie', 'Krimi', 'Dokumentarfilm', 'Drama', 'Familie', 'Fantasy', 
'Historie', 'Horror', 'Musik', 'Mystery', 'Liebesfilm', 'Science Fiction', 'TV-Film', 'Thriller', 'Kriegsfilm', 'Western']
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/help')
def help_():
    return f'''
            <h1>Search-n-Watch Help</h1>
            <a href='https://www.google.com/'><button>Search for answers</button></a>
            <a href='/'><button>Home</button></a>
            
'''
@app.route('/find')
def find():
    return render_template('preset.html', page_name='Find Media', page_content = 'Find media for you ! (W.I.P)')
@app.route('/search')
def search():
    return render_template('preset.html', page_name='Search', page_content='W.I.P')
@app.route('/random_movie')
def random_movie():
    random_mov = recommender.format_media_data(recommender.get_random_movie_from_genres(all_movie_genres))
    return render_template('preset.html', page_name='Random Movie', page_content=random_mov)
app.run(debug=True)