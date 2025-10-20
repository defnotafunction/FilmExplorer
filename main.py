from flask import Flask, render_template, request, redirect, url_for
import json
from itertools import chain
app = Flask(__name__)
from findingmediaheckyeah import MediaRecommender, search_for_show, get_media_from_id, search_for_movie
with open('userdata.json') as data:
    user_data = json.load(data)
def save_user_data(data):
    with open('userdata.json', 'w') as d:
        json.dump(data, d, indent=4)
def end_app(username):
    user_data[username]['logged_in'] = False
    save_user_data(user_data)
recommender = MediaRecommender()
logged_in = False
@app.route('/')
def home():
    return render_template('index.html', page_name='Home')
@app.route('/help')
def help_():
    return render_template('preset.html', page_name='Help')
@app.route('/find')
def find():
    return render_template('find.html', page_name='Find Media', page_content = 'Find media for you ! (W.I.P)')
@app.route('/browse', methods=['GET', 'POST'])
def browse():
    if request.method == 'POST':
        return redirect(url_for('search', keywords=request.form['search']))
    return render_template('browse.html', page_name='Browse', page_content='Browse movies and shows!')
@app.route('/search')
def search(query):
    #returns a list with media names
    query = request.args.get('search')
    if query:
        media_found = sorted([recommender.format_media_dict(dct, 'show') if dct in search_for_show(query)['results'] else recommender.format_media_dict(dct, 'movie') for dct in chain(search_for_movie(query)['results'],search_for_show(query)['results'])], reverse=True, key=lambda x: x['rating'])
        return render_template('search.html', media_found=media_found, page_name='Search')
@app.route('/random-movie')
def random_movie():
    random_mov = recommender.format_media_dict(recommender.get_random_movie(), 'movie')
    return render_template('base_media.html', page_name='Random Movie', media_info=random_mov, media_title=random_mov['title'])
@app.route('/media/<media_type>/<media_name>/<int:id>')
def media_page(media_type, media_name, id):
    media_info = recommender.format_media_dict(get_media_from_id(id, media_type), media_type)
    return render_template('base_media.html', page_name=f"Media Page - {media_name}", media_info=media_info, media_name=media_name)
@app.route('/random-show')
def random_show():
    random_show = recommender.format_media_dict(recommender.get_random_show(), 'show')
    return render_template('base_media.html', page_name='Random Show', media_info=random_show, media_title=random_show['title'])
@app.route('/user/<username>')
def userpage(username):
    if not user_data[username]['logged_in']:
        return redirect(url_for("login"))
    user_data[username]['logged_in'] = False
    return render_template('user.html', username=username, page_name='Account')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in user_data:
            if user_data[request.form['username']]['password'] == request.form['password'] and not user_data[request.form['username']]['logged_in']:
                user_data[request.form['username']]['logged_in']= True
                return redirect(url_for('userpage', username=request.form['username']))
    
    return render_template('login.html', page_name = 'Login')
@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.form['username'] not in user_data:
            user_data[request.form['username']] = {'password': request.form['password'], 'banned': False, 'logged_in': True}
            save_user_data(user_data)
            return redirect(url_for('userpage', username=request.form['username']))

    return render_template('login.html', page_name = 'Sign up')
if __name__ == '__main__':
    app.run(debug=True)
