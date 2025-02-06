from flask import Flask, render_template, request
import os
import pickle
import pandas as pd
import requests

# URLs of the .pkl files from GitHub Releases
MOVIES_DICT_URL = "https://github.com/nishanlimbuchemjong/Movie-Recommender-System/releases/download/v1.0/movies_dict.pkl"
SIMILARITY_URL = "https://github.com/nishanlimbuchemjong/Movie-Recommender-System/releases/download/v1.0/similarity.pkl"

# Function to download missing files
def download_file(url, filename):
    if not os.path.exists(filename):  # Check if file exists
        print(f"Downloading {filename}...")
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"{filename} downloaded successfully.")

# Ensure model directory exists
os.makedirs("model", exist_ok=True)

# Download model files if they don't exist
download_file(MOVIES_DICT_URL, "model/movies_dict.pkl")
download_file(SIMILARITY_URL, "model/similarity.pkl")

# Load the model files
movies_dict = pickle.load(open('model/movies_dict.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# function to get the poster of the movies from IMBD Movie API
def fetch_poster(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=35333bca71e434fd913bc003bca924ab&language=en-US".format(movie_id))
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
    # finding the index of the movie
    movie_index = movies[movies['title'] == movie].index[0]

    # finding the similarity distance ot the given movie
    distance = similarity[movie_index]
    
    # finding the distances that are similar to the given movie
    # Here, enumerate() is used to track the index of each moviews when sorting them
    # key = lambda x: x[1] -> is used to get the second elements when sorted
    movie_list = sorted(list(enumerate(distance)), reverse=True, key = lambda x: x[1])[1:31]
    
    recommendation_list = []
    recommended_poster = []
    # getting all the movie_list which is contains in list of tuples and assigning in recommendation_list
    # new_df.iloc[i[0]].title --> this gets all the movies title from the list of tuples. here i[0] -> is the first elemnent of the tuple given
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id

        recommendation_list.append(movies.iloc[i[0]].title)
        # fetch movie poster from API
        recommended_poster.append(fetch_poster(movie_id))
    return recommendation_list, recommended_poster

app = Flask(__name__)

@app.route('/')
def home():
    all_movies_title = movies['title'].head(150).tolist()
    all_movies_poster = [fetch_poster(id) for id in movies['movie_id'].head(150)]
    all_movies = zip(all_movies_title, all_movies_poster)
    return render_template('index.html', all_movies=all_movies)
    # return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie_name = request.form.get('movie_name')
    if movie_name:
        recommendations = recommend(movie_name)
        movie_names, posters = recommendations
        movies_with_posters = zip(movie_names, posters)
        return render_template('recommendation.html', recommendations=movies_with_posters)
    else:
        return "No movies found"

if __name__ == '__main__':
    app.run(debug=True)