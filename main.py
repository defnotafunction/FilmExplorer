from flask import Flask, render_template, request, redirect, url_for, session, abort
from itertools import chain
from findingmediaheckyeah import MediaRecommender, search_for_show, get_media_from_id, search_for_movie
from forms import *
from extensions import db
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
from tools import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select


recommender = MediaRecommender()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_AND_DIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html', page_name='Home')

@app.route('/help')
def help_():
    return render_template('preset.html', page_name='Help')

@app.route('/find')
def find():
    return render_template('find.html',
                            page_name='Find Media',
                            page_content = 'Find media for you ! (W.I.P)')

@app.route('/browse', methods=['GET', 'POST'])
def browse():
    search_form = Searchbar()
    try:
        if search_form.validate_on_submit():
            return redirect(url_for('search', page_num=1, query=search_form.query.data))

    finally:
        return render_template('browse.html',
                                page_name='Browse',
                                page_content='Browse movies and shows!',
                                form=search_form)

@app.route('/search/<int:page_num>')
def search(page_num):
    # returns a list with media names
    query = request.args.get('query')

    if not query:
        return redirect(url_for('home'))

    media_found = recommender.get_media_from_query(query, page_num)
    
    return render_template(
        'search.html',
        media_found=media_found,
        page_name='Search',
        page_num=page_num,
        query=query
    )

@app.route('/random-movie')
def random_movie():
    random_mov = recommender.format_media_dict(data=recommender.get_random_movie(),
                                                type_of_media='movie'
                                                )
    
    return render_template('base_media.html',
                            page_name='Random Movie',
                            media_info=random_mov,
                            media_title=random_mov['title']
                        )

@app.route('/media/<media_type>/<media_name>/<int:id>', methods=['GET', 'POST'])
def media_page(media_type, media_name, id):
    like_form = LikeButton()

    if (like_form.validate_on_submit()
        and like_form.submit.data
        and current_user.is_authenticated):
        new_media_obj = Media(user_id=current_user.id,
                          media_id=id,
                          media_type=media_type
                          )
        
        current_user.liked_media.append(new_media_obj)
        db.session.commit()

    media_info = recommender.format_media_dict(
        get_media_from_id(id, media_type),
          media_type
          )
    
    return render_template('base_media.html',
                            page_name=f"Media Page - {media_name}", 
                            media_info=media_info, media_name=media_name,
                            like_form=like_form,
                            current_user = current_user
                            )

@app.route('/random-show')
def random_show():
    random_show = recommender.format_media_dict(data=recommender.get_random_show(),
                                                 type_of_media='show'
                                                 )
    
    return render_template('base_media.html',
                            page_name='Random Show',
                            media_info=random_show,
                            media_title=random_show['title'])

@app.route('/user/<username>')
def userpage(username):
    remove_like_form = RemoveLike()
    # checks if user exists otherwise throws 404 error
    if not check_if_user_exists(username):
        abort(404)

    viewed_user = db.session.execute(
        select(User).where(User.username == username)
        ).scalar_one()

    if viewed_user == current_user:
        display_private_info = True
    else:
        display_private_info = False

    liked_media = []
    for media in viewed_user.liked_media:
        media_dict = recommender.format_media_dict(
            data=get_media_from_id(media.media_id, media.media_type),
            type_of_media=media.media_type
            )

        liked_media.append(media_dict)

    return render_template('user.html',
                            username=username,
                            page_name='Account',
                            display_private=display_private_info,
                            liked_media=liked_media,
                            remove_like_form = remove_like_form
                            )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('userpage', username=current_user.username))

    login_form = LoginForm()
    error_message = ''

    if login_form.validate_on_submit():
        user_to_login = get_user_from_username(login_form.username.data)

        if check_password_hash(user_to_login.hashed_password, login_form.password.data):
            login_user(user_to_login, remember=True)
            return redirect(url_for('userpage', username=user_to_login.username))
        
        error_message = 'Incorrect username or password'

    return render_template('login.html', page_name = 'Login', form=login_form, message=error_message)

@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    signup_form = SignUpForm()
    error_message = ''

    if signup_form.validate_on_submit():
            if not check_if_user_exists(signup_form.username.data):
                user_obj = User(username=signup_form.username.data,
                                hashed_password=generate_password_hash(signup_form.password.data)
                                )  # create a new user
                safe_db_add(user_obj)  # add user to data base
                login_user(user_obj)  # login user
                
                return redirect(url_for('userpage', username=signup_form.username.data))

            error_message = 'Username already in use!'
            
    return render_template('login.html', page_name = 'Sign Up', form=signup_form, message=error_message)

@app.route('/user/<username>/remove-liked/<int:media_id>/<media_type>', methods=['POST'])
@login_required
def remove_liked(username, media_id, media_type):
    if current_user.username != username:
        abort(403)

    media_to_remove = next(
        (m for m in current_user.liked_media 
         if m.media_id == media_id and m.media_type == media_type),
        None
    )

    if media_to_remove:
        current_user.liked_media.remove(media_to_remove)
        db.session.commit()

    return redirect(url_for('userpage', username=username))


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/gag')
def run_gag():
    return render_template('gag.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)

