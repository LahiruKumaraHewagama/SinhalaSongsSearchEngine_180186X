from elasticsearch import Elasticsearch, helpers
import json
from flask import Flask
from wtforms import Form, StringField, SelectField
from flask import flash, render_template, request, redirect, jsonify
import re
from googletrans import Translator
from elastic_search_indexing.search import search_query_filtered, search_query

es = Elasticsearch("localhost:9200")
app = Flask(__name__)


global_search = "dada"
global_artists = []
global_genre = []
global_music = []
global_lyricist = []
global_targetDomain = []
global_sourceDomain = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global global_search
    global global_artists
    global global_genre
    global global_music
    global global_lyricist
    global global_targetDomain 
    global global_sourceDomain 
    if request.method == 'POST':
        if 'form_1' in request.form:            
            if request.form['query']:
                search = request.form['query']
                global_search = search
                print(global_search)
            else :
                search = global_search
            list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain= search_query(search)
            global_artists, global_genre, global_music, global_lyricist,global_targetDomain ,global_sourceDomain = artists, genres, music, lyricist,targetDomain ,sourceDomain

        elif 'filter' in request.form:
            search = global_search
            artist_filter = []
            genre_filter = []
            music_filter = []
            lyricist_filter = []
            targetDomain_filter=[]
            sourceDomain_filter=[]
            for i in global_artists :          
                if request.form.get(i["key"]):                 
                    artist_filter.append(i["key"])
            for i in global_genre :
                if request.form.get(i["key"]):
                    genre_filter.append(i["key"])
            for i in global_music:
                if request.form.get(i["key"]):
                    music_filter.append(i["key"])
            for i in global_lyricist:
                if request.form.get(i["key"]):
                    lyricist_filter.append(i["key"])
            for i in global_targetDomain:
                if request.form.get(i["key"]):
                    targetDomain_filter.append(i["key"])
            for i in global_sourceDomain:
                if request.form.get(i["key"]):
                    sourceDomain_filter.append(i["key"])

            list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain= search_query_filtered(search, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter)
            print(search)
            print(artist_filter)
            print(genre_filter)
            print(music_filter)
            print(targetDomain_filter)
            print(sourceDomain_filter)
        return render_template('index.html',count=len(list_songs), songs = list_songs, artists = artists, genres = genres, music = music, lyricist = lyricist,targetDomain=targetDomain ,sourceDomain=sourceDomain)
    return render_template('index.html', count=0,songs = '', artists = '',  genres = '', music = '', lyricist = '',targetDomain='',sourceDomain='')

if __name__ == "__main__":
    app.run(debug=True)
