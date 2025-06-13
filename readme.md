# Movie Analysis Tool

A comprehensive TMDB API analyser that collects key film metrics including revenue, budget, release dates, and genre distribution, then transforms the data into visual insights about box office trends and industry patterns.

### Tech Stack
- Language: Python 
- Libraries:
  - requests
  - pandas
  - matplotlib
  - python-dotenv
- Data Source: TMDB API

### How to Run
> Prerequisites
- Python 3.7+ installed
- TMDB API key

1. ### Clone or Download the Project
```
git clone https://github.com/Kevvy404/Movie-Analysis-Tool.git
cd Movie-Analysis-Tool
```
2. ### Getting your API key
Go to https://developer.themoviedb.org/v4/docs/getting-started and register for an API key

3. ### Create .env file
```
TMDB_API_KEY = YOUR_API_KEY
TMDB_BASE_URL = https://api.themoviedb.org/3
MAX_RESULTS = 100
```

4. ### Running the program
Now you can run the program by using:
```
python -u main.py
```