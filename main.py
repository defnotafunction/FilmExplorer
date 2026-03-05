from flask import Flask, render_template, request, redirect, url_for, flash, abort
from tmdb_api import MediaRecommender, get_media_from_id
from forms import *
from extensions import db
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
from tools import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select
import os

recommender = MediaRecommender()

# App configuration.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_AND_DIFICATIONS'] = False

# Initalizing login_manager.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Default page.
@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html', page_name='Home')

@app.route('/help')
def help_():
    return render_template('preset.html', page_name='Help')

@app.route('/find')
@login_required
def find():
    return render_template('find.html',
                            page_name='Find Media',
                            page_content = 'Find media based on your likes!'
                            )

@app.route('/find/recommended-media/<media_filter>')
@login_required
def recommended_media(media_filter):
    if media_filter not in ['show', 'movie', 'all']:
        abort(404)

    liked_ids = [(l.media_id, l.media_type) for l in current_user.liked_media]
    
    if len(liked_ids) <= 2:
        flash("You don't have enough liked titles!", 'error')
        return redirect(url_for('find'))

    recommended_ids = recommender.recommend(liked_ids, type_of_media_to_recommend=media_filter)
    media_found = [
                    recommender.format_media_dict(get_media_from_id(_id, type_of_media),
                                                type_of_media
                                                )
                    for (_id, type_of_media) in recommended_ids
                    ]
    
    return render_template('recommended_media.html',
                            page_name = 'Recommendations',
                            media_found=media_found)


@app.route('/browse', methods=['GET', 'POST'])
def browse():
    search_form = Searchbar()

    if search_form.validate_on_submit():
        return redirect(url_for(
                                'search_media',
                                page_num=1,
                                query=search_form.query.data)
                                )

    return render_template(
                            'browse.html',
                            page_name='Browse',
                            form=search_form
                            )

@app.route('/users/<query>')
def search_user(query):
    feteched_users = get_users_from_query(query)
    
    return render_template(
                        'search_user.html',
                        query=query,
                        fetched_users=feteched_users
                        )


@app.route('/search/<query>/<int:page_num>')
def search_media(query, page_num):
    like_form = LikeButton()
    media_found = recommender.get_media_from_query(query, page_num)
    
    for m in media_found: 
            
        
        if not current_user.is_authenticated:
            m['liked_status'] = None  # Not logged in
            continue

        in_user_liked = check_media_obj_in_user_liked(m['id'], current_user)
        
        if in_user_liked:
            m['liked_status'] = 'Already liked'
        else:
            m['liked_status'] = True  # Able to be liked

    return render_template(
        'search_media.html',
        media_found=media_found,
        page_name='Search',
        page_num=page_num,
        query=query,
        like_form=like_form
    )

@app.route('/random-movie')
def random_movie():
    random_mov = recommender.format_media_dict(data=recommender.get_random_movie(),
                                                type_of_media='movie'
                                                )
    
    return render_template(
                            'base_media.html',
                            page_name='Random Movie',
                            media_info=random_mov,
                            media_title=random_mov['title']
                        )

@app.route('/media/<media_type>/<media_name>/<int:media_id>', methods=['GET', 'POST'])
def media_page(media_type, media_name, media_id):
    like_form = LikeButton()

    if like_form.validate_on_submit():
        new_media_obj = Media(user_id=current_user.id,
                          media_id=media_id,
                          media_type=media_type
                          )

        current_user.liked_media.append(new_media_obj)
        db.session.commit()

    media_info = recommender.format_media_dict(
        get_media_from_id(media_id, media_type),
          media_type
          )
    
    return render_template('base_media.html',
                            page_name=f"Media Page - {media_name}", 
                            media_info=media_info,
                            media_name=media_name,
                            media_id = media_id,
                            like_form=like_form,
                            current_user = current_user,
                            check_media_obj_in_user_liked = check_media_obj_in_user_liked
                            )


@app.route('/user/<username>')
def userpage(username):
    remove_like_form = RemoveLike()
    
    if not check_if_user_exists(username):
        abort(404)

    viewed_user = db.session.execute(
        select(User).where(User.username == username)
        ).scalar_one()

    if viewed_user == current_user:
        display_private_info = True
    else:
        display_private_info = False

    # LOADING UP USER'S LIKED MEDIA:

    liked_media = []
    
    for media in viewed_user.liked_media:
        media_dict = recommender.format_media_dict(
            data=get_media_from_id(media.media_id, media.media_type),
            type_of_media=media.media_type
            )

        liked_media.append(media_dict)

    return render_template(
                            'user.html',
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
   

    if login_form.validate_on_submit():
        if not check_if_user_exists(login_form.username.data):
            print('user dont exist')
            flash('User does not exist!', 'error')
            return redirect(url_for('login'))

        user_to_login = get_user_from_username(login_form.username.data)

        if check_password_hash(user_to_login.hashed_password, login_form.password.data):
            login_user(user_to_login, remember=True)
            return redirect(url_for('userpage', username=user_to_login.username))
        
        flash('Wrong username or password', 'error')
        redirect(url_for('login'))

    return render_template('login.html', page_name = 'Login', form=login_form)

@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    signup_form = SignUpForm()

    if signup_form.validate_on_submit():
            if not check_if_user_exists(signup_form.username.data):
                user_obj = User(
                    username=signup_form.username.data,
                    hashed_password=generate_password_hash(signup_form.password.data)
                                )  # Create a new user
                
                # TEMPORARY
                if user_obj.username == 'aiden':
                    user_obj.role = 'admin'

                safe_db_add(user_obj)  # Add user to data base
                login_user(user_obj)  # Login user
                
                return redirect(url_for('userpage', username=signup_form.username.data))

            flash('Username already in use!', 'error')
            return redirect(url_for('signup'))

    return render_template('login.html', page_name = 'Sign Up', form=signup_form)

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
@app.route('/like/<int:media_id>/<media_type>/<query>/<page_num>', methods=['POST'])
def like_title_from_search(media_id, media_type, query, page_num):
    new_media_obj = Media(
                        user_id=current_user.id,
                        media_id=media_id,
                        media_type=media_type
                          )

    current_user.liked_media.append(new_media_obj)
    db.session.commit()

    return redirect(url_for('search_media', query=query, page_num=page_num))

@login_required
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # TESTING ADMIN ROUTE
    delete_user_form = DeleteUserForm()

    if current_user.role != 'admin':
        abort(403)

    if delete_user_form.validate_on_submit():
        delete_user_from_name(delete_user_form.query.data)

    return render_template(
                            'admin_dashboard.html',
                            page_name='Admin Dashboard',
                            page_content='no exploting power pls',
                            delete_form = delete_user_form
                            )


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)

