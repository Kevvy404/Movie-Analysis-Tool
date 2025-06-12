if not API_KEY:
    print("Error: TMDB_API_KEY not found in .env!")
else:
    print("API Key loaded successfully!")
    print(f"Key (partial): {API_KEY[:5]}...") 