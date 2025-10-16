# Search-n-Watch! - Movie & TV Show Recommender

## Overview
A Flask web application that helps users discover movies and TV shows using The Movie Database (TMDB) API. Features include random movie/show recommendations, user authentication, and personalized suggestions.

## Recent Changes
- **2025-10-16**: Configured for deployment
  - Fixed port conflict issues  
  - Set up deployment configuration for autoscale
  - Flask app running successfully on port 5000

## Project Structure
- `main.py` - Flask application with routes and user authentication
- `findingmediaheckyeah.py` - MediaRecommender class with TMDB API integration
- `templates/` - HTML templates for all pages
- `userdata.json` - User authentication data

## Features
- Random movie and TV show recommendations
- User login and signup
- Browse media by genres
- Integration with TMDB API for movie/show data

## How to Run
The Flask app runs automatically via the configured workflow, or you can run:
```bash
python main.py
```

## Deployment
The app is configured for deployment using autoscale. Click the Deploy/Publish button in Replit to make your app live!
