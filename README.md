# Film Explorer
Film Explorer is a website that helps curious users find movies and shows that fits their preferences.

## Features
- Authentication and Authorization - Secure user sign up and login using `flask-SQLAlchemy` and `flask-login`.
- Database - Powered by SQLALCHEMY.
- Frontend - Built with HTML, CSS, and Jinja2.
- Backend - Flask + Python handles users and API requests. 
- Media Browsing - Browse movies and shows powered by TMDB API.
- Liking - Add and remove shows and movies from your "Liked Titles" list. Powered by SQLALCHEMY.
- Recommender System - Recommends media based on what you've liked. Powered by `scikit-learn`'s KNeighborsClassifer.

## Project Structure

```
├── main.py              # [Route logic]
├── models.py            # [SQLAlchemy Models]
├── forms.py             # [Flask Forms]
├── tools.py             # [Helper functions]
├── tmdb_api.py          # [Requests to TMDB API]
├── extensions.py        # [Location of SQLAlchemy object]
├── static/              # [CSS and static assets]
├── templates/           # [HTML templates]
├── instance/            # [DB file]
└── pyproject.toml       # [Project configuration]
```

## Technologies Used
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- WTForms
- SQLAlchemy
- Requests
- NumPy
- Scikit-learn
- Python-dotenv
- TMDB API
- Jinja2
- HTML/CSS


## License
This project is not available for public use or distribution.

## Author
Name: Nkola Katambwa
Email Account: aykendevs@gmail.com