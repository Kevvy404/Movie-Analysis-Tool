import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = os.getenv('TMDB_BASE_URL')

def get_movie_info(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {'api_key': API_KEY}
    response = requests.get(url, params = params)
    response.raise_for_status()
    return response.json()

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        'api_key' : API_KEY,
        'query' : query,
        'language' : 'en-UK',
        'page' : 5
    }

    response = requests.get(url, params = params)
    response.raise_for_status()
    return response.json()

# def get_popular_movies():
#     url = f"{BASE_URL}/movie/popular" 
#     params = {'api_key': API_KEY}
#     response = requests.get(url, params = params)
#     response.raise_for_status()
#     return response.json()

def get_multiple_pages_of_popular_movies(pages=5):
    all_movies = []
    for page in range(1, pages+1):
        url = f"{BASE_URL}/movie/popular"
        params = {
            'api_key': API_KEY,
            'page': page
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        all_movies.extend(response.json()['results'])
    return all_movies

def get_user_input():
    while True:
        try:
            num_movies = int(input("How many movies would you like to analyze? (1-100): "))
            if 1 <= num_movies <= 100:
                return num_movies
            else:
                print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")

##############################################################
#                       Data Analysis                       #
##############################################################

def genre_distro(movies):
    genre_count = {}

    for movie in movies:
        for genre in movie.get('genres', []):
            genre_name = genre['name']
            genre_count[genre_name] = genre_count.get(genre_name, 0) + 1

    df = pd.DataFrame(list(genre_count.items()), columns = ['Genre', 'Count'])
    df = df.sort_values('Count', ascending = False)

    return df

def revenue_vs_rating_distro(movies):
    data = []
    for movie in movies:
        if movie.get('revenue', 0) > 0 and movie.get('vote_average', 0) > 0:
            data.append({
                'title': movie.get('title'),
                'revenue': movie.get('revenue'),
                'rating': movie.get('vote_average'),
                'vote_count': movie.get('vote_count')
            })
    
    df = pd.DataFrame(data)
    return df

#############################################################
#                       Visualisation                       #
#############################################################

def plot_genre_distro(genre_df):
    plt.figure(figsize=(10, 6))
    plt.bar(genre_df['Genre'], genre_df['Count'])
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.title('Genre Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_revenue_vs_rating(revenue_df):
    plt.figure(figsize=(10, 6))
    plt.scatter(revenue_df['rating'], revenue_df['revenue']/1e6, alpha=0.5)
    plt.xlabel('Rating')
    plt.ylabel('Revenue (Millions USD)')
    plt.title('Revenue vs Rating')
    plt.grid(True)
    plt.show()

def analyse_genre(num_movies):
    pages_needed = (num_movies + 19) // 20  # Round up division
    
    print(f"Fetching {num_movies} movies for analysis...")
    
    # Get popular movies (this returns a list directly)
    movies = get_multiple_pages_of_popular_movies(pages=pages_needed)
    
    detailed_movies = []
    # Limit to user-specified number of movies
    for i, movie in enumerate(movies[:num_movies], 1):
        try:
            print(f"Fetching details for movie {i}/{num_movies}: {movie.get('title', 'Unknown')}")
            details = get_movie_info(movie['id'])
            detailed_movies.append(details)
        except Exception as e:
            print(f"Error getting details for movie ID {movie['id']}: {e}")
            continue
    
    if not detailed_movies:
        print("No movie details were successfully fetched. Exiting.")
        return None
    
    print(f"\nSuccessfully analysed {len(detailed_movies)} movies!")
    
    genre_df = genre_distro(detailed_movies)
    print("\nGenre Distribution:")
    print("==========================")
    print(genre_df)
    print("==========================")
    plot_genre_distro(genre_df)

    return genre_df

def analyse_revenue_vs_rating(num_movies):
    pages_needed = (num_movies + 19) // 20  # Round up division
    
    print(f"Fetching {num_movies} movies for revenue vs rating analysis...")
    
    # Get popular movies (this returns a list directly)
    movies = get_multiple_pages_of_popular_movies(pages=pages_needed)
    
    detailed_movies = []
    # Limit to user-specified number of movies
    for i, movie in enumerate(movies[:num_movies], 1):
        try:
            print(f"Fetching details for movie {i}/{num_movies}: {movie.get('title', 'Unknown')}")
            details = get_movie_info(movie['id'])
            detailed_movies.append(details)
        except Exception as e:
            print(f"Error getting details for movie ID {movie['id']}: {e}")
            continue
    
    if not detailed_movies:
        print("No movie details were successfully fetched. Exiting.")
        return None
    
    print(f"\nSuccessfully analysed {len(detailed_movies)} movies!")
    
    revenue_df = revenue_vs_rating_distro(detailed_movies)
    
    if revenue_df.empty:
        print("No movies with valid revenue and rating data found.")
        return None
    
    print(f"\nRevenue vs Rating Analysis ({len(revenue_df)} movies with valid data):")
    print("=" * 60)
    print(f"Average Revenue: ${revenue_df['revenue'].mean():,.0f}")
    print(f"Average Rating: {revenue_df['rating'].mean():.2f}")
    print(f"Highest Revenue: {revenue_df.loc[revenue_df['revenue'].idxmax(), 'title']} (${revenue_df['revenue'].max():,.0f})")
    print(f"Highest Rating: {revenue_df.loc[revenue_df['rating'].idxmax(), 'title']} ({revenue_df['rating'].max():.1f})")
    print("=" * 60)
    
    # Show correlation
    correlation = revenue_df['revenue'].corr(revenue_df['rating'])
    print(f"Correlation between Revenue and Rating: {correlation:.3f}")
    
    plot_revenue_vs_rating(revenue_df)
    
    return revenue_df

def main():
    num_movies = get_user_input()
    
    analysis_choice = input("Choose analysis type (1: Genre, 2: Revenue vs Rating): ")
    
    if analysis_choice == "1":
        analyse_genre(num_movies)
    elif analysis_choice == "2":
        analyse_revenue_vs_rating(num_movies)
    else:
        print("Invalid choice. Running genre analysis by default.")
        analyse_genre(num_movies)

    # if not API_KEY:
    #     print("Error: TMDB_API_KEY not found in .env!")
    # else:
    #     print("API Key loaded successfully!")
    #     print(f"Key (partial): {API_KEY[:5]}...") 

    # popular_movies = get_multiple_pages_of_popular_movies(pages=3)
    # movies = get_multiple_pages_of_popular_movies(pages=amount)

    # detailed_movies = []
    # for i, movie in enumerate(movies[:amount], 1):
    #     details = get_movie_info(movie['id'])
    #     detailed_movies.append(details) 

    # genre_df = genre_distro(detailed_movies)

    # print("\nGenre Distribution:")
    # print("==========================")
    # print(genre_df)
    # print("==========================")

    # plot_genre_distro(genre_df)

if __name__ == "__main__":
    main()