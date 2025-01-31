from flask import Flask, render_template, request
import pickle
import pandas as pd

movies_dict = pickle.load(open('model/movies_dict.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)



def recommend(movie):
    # finding the index of the movie
    movie_index = movies[movies['title'] == movie].index[0]

    # finding the similarity distance ot the given movie
    distance = similarity[movie_index]
    
    # finding the distances that are similar to the given movie
    # Here, enumerate() is used to track the index of each moviews when sorting them
    # key = lambda x: x[1] -> is used to get the second elements when sorted
    movie_list = sorted(list(enumerate(distance)), reverse=True, key = lambda x: x[1])[1:6]
    
    recommendation_list = []
    # getting all the movie_list which is contains in list of tuples and assigning in recommendation_list
    # new_df.iloc[i[0]].title --> this gets all the movies title from the list of tuples. here i[0] -> is the first elemnent of the tuple given
    for i in movie_list:
        recommendation_list.append(movies.iloc[i[0]].title)
    return recommendation_list

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie_name = request.form.get('movie_name')
    if movie_name:
        recommendations = recommend(movie_name)
        return render_template('index.html', recommendations=recommendations)
    else:
        return "No movies found"

if __name__ == '__main__':
    app.run(debug=True)