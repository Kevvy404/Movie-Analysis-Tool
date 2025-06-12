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
        'language' : 'en-US',
        'page' : 1
    }

    response = requests.get(url, params = params)
    response.raise_for_status()
    return response.json()

def search_and_select_movie():
    """Search for movies by title and let user select one"""
    while True:
        movie_title = input("Enter movie title to search: ").strip()
        if not movie_title:
            print("Please enter a valid movie title.")
            continue
            
        try:
            search_results = search_movies(movie_title)
            movies = search_results.get('results', [])
            
            if not movies:
                print(f"No movies found for '{movie_title}'. Try a different search term.")
                retry = input("Would you like to search again? (y/n): ").lower()
                if retry != 'y':
                    return None
                continue
            
            # Display search results
            print(f"\nFound {len(movies)} movies matching '{movie_title}':")
            print("-" * 60)
            
            for i, movie in enumerate(movies[:10], 1):  # Show max 10 results
                title = movie.get('title', 'Unknown Title')
                release_date = movie.get('release_date', 'Unknown')
                year = release_date[:4] if release_date and release_date != 'Unknown' else 'Unknown'
                rating = movie.get('vote_average', 0)
                
                print(f"{i}. {title} ({year}) - Rating: {rating}/10")
            
            print("-" * 60)
            
            while True:
                try:
                    choice = input(f"Select a movie (1-{min(len(movies), 10)}) or 's' to search again: ").strip()
                    
                    if choice.lower() == 's':
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= min(len(movies), 10):
                        selected_movie = movies[choice_num - 1]
                        return selected_movie['id']
                    else:
                        print(f"Please enter a number between 1 and {min(len(movies), 10)}")
                        
                except ValueError:
                    print("Please enter a valid number or 's' to search again")
            
            continue
            
        except Exception as e:
            print(f"Error searching for movies: {e}")
            retry = input("Would you like to try again? (y/n): ").lower()
            if retry != 'y':
                return None
            
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

def user_selection():
    while True:
        try:
            print("\n" + "="*50)
            print("TMDB MOVIE TOOL")
            print("="*50)
            print("1. Movie Information")
            print("2. Movie Analysis") 
            print("3. Exit")
            print("="*50)
            
            selection = int(input("Select 1, 2 or 3: "))
            
            if selection == 1:
                print("\n" + "="*50)
                print("MOVIE SEARCH")
                print("="*50)
                
                movie_id = search_and_select_movie()
                
                if movie_id is None:
                    print("Movie search cancelled.")
                    continue
                
                try:
                    movie_data = get_movie_info(movie_id)
                    print("\n" + "="*50)
                    print("MOVIE INFORMATION")
                    print("="*50)
                    print(f"Title: {movie_data.get('title', 'N/A')}")
                    print(f"Release Date: {movie_data.get('release_date', 'N/A')}")
                    print(f"Rating: {movie_data.get('vote_average', 'N/A')}/10")
                    print(f"Runtime: {movie_data.get('runtime', 'N/A')} minutes")
                    print(f"Budget: ${movie_data.get('budget', 0):,}")
                    print(f"Revenue: ${movie_data.get('revenue', 0):,}")

                    genres = [genre['name'] for genre in movie_data.get('genres', [])]
                    print(f"Genres: {', '.join(genres) if genres else 'N/A'}")
                    
                    overview = movie_data.get('overview', 'N/A')
                    print(f"Overview: {overview[:500]}{'...' if len(overview) > 500 else ''}")
                    print("="*50)
                    
                except Exception as e:
                    print(f"Error fetching movie information: {e}")

                continue_choice = input("\nWould you like to do something else? (y/n): ").lower()
                if continue_choice != 'y':
                    break

            elif selection == 2:
                # Movie Analysis - add the analysis choice here
                print("\n" + "="*40)
                print("MOVIE ANALYSIS OPTIONS")
                print("="*40)
                print("1. Genre Distribution Analysis")
                print("2. Revenue vs Rating Analysis")
                print("="*40)

                try:
                    analysis_choice = int(input("Choose analysis type (1 or 2): "))
                    num_movies = get_user_input()
                    
                    if analysis_choice == 1:
                        print("\nStarting Genre Analysis...")
                        analyse_genre(num_movies)
                    elif analysis_choice == 2:
                        print("\nStarting Revenue vs Rating Analysis...")
                        analyse_revenue_vs_rating(num_movies)
                    else:
                        print("Invalid choice. Running genre analysis by default.")
                        analyse_genre(num_movies)
                        
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue
            
                continue_choice = input("\nWould you like to do something else? (y/n): ").lower()
                if continue_choice != 'y':
                    break

            elif selection == 3:
                print("Thank you for using the TMDB Movie Tool!")
                break
            else:
                print("Invalid selection. Please choose 1, 2, or 3.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nExiting... Thank you for using the TMDB Movie Tool!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def get_user_input():
    while True:
        try:
            num_movies = int(input("How many movies would you like to analyse? (1-100): "))
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
    pages_needed = (num_movies + 19) // 20 
    print(f"Fetching {num_movies} movies for analysis...")

    movies = get_multiple_pages_of_popular_movies(pages=pages_needed)
    detailed_movies = []

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
    print("="*50)
    print(genre_df)
    print("="*50)
    plot_genre_distro(genre_df)

    return genre_df

def analyse_revenue_vs_rating(num_movies):
    pages_needed = (num_movies + 19) // 20
    
    print(f"Fetching {num_movies} movies for revenue vs rating analysis...")
    
    movies = get_multiple_pages_of_popular_movies(pages=pages_needed)
    detailed_movies = []

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
    user_selection()

if __name__ == "__main__":
    main()