from imdb import Cinemagoer

ia = Cinemagoer()

movie_id = '0133093'
movie = ia.get_movie(movie_id)

print("All available information")
print("=" * 50)

for key, value in movie.items():
    print(f"{key}: {value}")

print("\n" + "=" * 50)
print("Available keys:")
print(list(movie.keys()))
