from elasticsearch import Elasticsearch, helpers
import json
import re
from googletrans import Translator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def translate_to_english(value):
	translator = Translator()
	english_term = translator.translate(value, dest='en')
	return english_term.text

def post_processing_text(results):
    list_songs = []
    for i in range(len(results['hits']['hits'])) :
        lyrics = json.dumps(results['hits']['hits'][i]['_source']["lyrics"], ensure_ascii=False)
        lyrics = lyrics.replace('"', '')
        lyrics = lyrics.replace("'", '')       
        lyrics = lyrics.replace('\\', '')
        lyrics = lyrics.replace('t', '')
        lyrics = lyrics.replace('\xa0', '')
        lyrics = "<br>".join(lyrics.split("n"))
        lyrics =  re.sub(r'(<br> )+', r'\1', lyrics)
        j = 0
        while True :
            if lyrics[j] == '<' or lyrics[j] == '>' or lyrics[j] == 'b' or lyrics[j] == 'r' or lyrics[j] == ' ':
                j += 1
            else :
                break
        lyrics = lyrics[j:]
        results['hits']['hits'][i]['_source']["lyrics"] = lyrics
        list_songs.append(results['hits']['hits'][i]['_source'])
    aggregations = results['aggregations']
    artists = aggregations['artist']['buckets']
    genres = aggregations['genre']['buckets']
    music = aggregations['music']['buckets']
    lyricist = aggregations['lyricist']['buckets']
    targetDomain = aggregations['Metaphors']['TargetDomain']['buckets']
    sourceDomain = aggregations['Metaphors']['SourceDomain']['buckets']
    print(targetDomain)
    

    return list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain


def search_text(search_term):
    results = es.search(index='sinhala-songs',body={
        "size" : 500,
    
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "multi_match": {
                                    "query": search_term,
                                    "fields": ["Metaphors.Metaphor","Metaphors.Meaning","Metaphors.SourceDomain","Metaphors.TargetDomain"]
                                }
                            }
                        } 
                    },
                    {
            "multi_match": {
                "query" : search_term,
                "type" : "best_fields",
                "fields" : [
                    "title_singlish","title_sinhala", "artist_name","genre",  "lyrics",
                    "lyricist", "music"]
                    
            }
                    }
                ]
            }
        },
        "aggs": {
        "Metaphors": {
            "nested": {
                "path": "Metaphors"
            },
            "aggs": {
                "TargetDomain": {
                    "terms": {
                        "field": "Metaphors.TargetDomain.keyword",
                        "size": 20
                    },
                    
                },
                 "SourceDomain": {
                    "terms": {
                        "field": "Metaphors.SourceDomain.keyword",
                        "size": 20
                    },
                    
                }
            }
        }
        ,
         "genre": {
                "terms": {
                    "field": "genre.keyword",
                    "size" : 15    
                }        
            },
            "artist": {
                "terms": {
                    "field":"artist_name.keyword",
                    "size" : 15
                }             
            },
            "music": {
                "terms": {
                    "field":"music.keyword",
                    "size" : 15
                }             
            },
            "lyricist": {
                "terms": {
                    "field":"lyricist.keyword",
                    "size" : 15
                }             
            },    
    }


    })
    print(results)
    list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain = post_processing_text(results)
    return list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain

def search_filter_text(search_term, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter):
    must_list = [                  
                    {
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "multi_match": {
                                    "query": search_term,
                                    "fields": ["Metaphors.Metaphor","Metaphors.Meaning","Metaphors.SourceDomain","Metaphors.TargetDomain"]
                                }
                            }
                        } 
                    },
                    {
                    "multi_match": {
                        "query" : search_term,
                        "type" : "best_fields",
                        "fields" : [
                            "title_singlish","title_sinhala", "artist_name","genre",  "lyrics",
                            "lyricist", "music"]                    
                    }
                    } 
        ]

    if len(artist_filter) != 0 :
        print("M")
        for i in artist_filter :
            print(i)
            must_list.append({"match" : {"artist_name" : {"query" : i }}})
    if len(genre_filter) != 0 :
        print("c")
        for i in genre_filter :
            must_list.append({"match" : {"genre":  {"query" : i }}})
    if len(music_filter) != 0 :
        print("g")
        for i in music_filter :
            must_list.append({"match" : {"music":  {"query" : i }}})
    if len(lyricist_filter) != 0 :
        print("w")
        for i in lyricist_filter :
            must_list.append({"match" : {"lyricist":  {"query" : i }}})
    if len(targetDomain_filter) != 0 :
        print("p")
        for i in targetDomain_filter :
            must_list.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.TargetDomain":  i 
                                }
                            }
                        } 
                    })
    if len(sourceDomain_filter) != 0 :
        print("z")
        for i in sourceDomain_filter :
            must_list.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.SourceDomain":  i 
                                }
                            }
                        } 
                    })

    results = es.search(index='sinhala-songs',body={
        "size" : 500,
        "query" :{
            "bool": {
                "must": must_list
            }
        } ,
        "aggs": {
        "Metaphors": {
            "nested": {
                "path": "Metaphors"
            },
            "aggs": {
                "TargetDomain": {
                    "terms": {
                        "field": "Metaphors.TargetDomain.keyword",
                        "size": 20
                    },
                    
                },
                 "SourceDomain": {
                    "terms": {
                        "field": "Metaphors.SourceDomain.keyword",
                        "size": 20
                    },
                    
                }
            }
        }
        ,
         "genre": {
                "terms": {
                    "field": "genre.keyword",
                    "size" : 15    
                }        
            },
            "artist": {
                "terms": {
                    "field":"artist_name.keyword",
                    "size" : 15
                }             
            },
            "music": {
                "terms": {
                    "field":"music.keyword",
                    "size" : 15
                }             
            },
            "lyricist": {
                "terms": {
                    "field":"lyricist.keyword",
                    "size" : 15
                }             
            },    
    }
    })
    list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain = post_processing_text(results)
    return list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain



def intent_classifier(search_term):

    select_type = False
    resultword = ''

    keyword_top = ["top", "best", "popular", "good", "great"]
    keyword_song = ["song", "sing", "sang", "songs", "sings"]
    keyword_targetDomain = ["metaphors"]
    search_term_list = search_term.split()
    for j in search_term_list : 
        documents = [j]
        documents.extend(keyword_top)
        documents.extend(keyword_song)
        documents.extend(keyword_targetDomain)
        tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)
        similarity_list = cs[0][1:]

        for i in similarity_list :
            if i > 0.8 :
                select_type  = True
    if select_type :
        querywords = search_term.split()
        querywords  = [word for word in querywords if word.lower() not in keyword_top]
        querywords  = [word for word in querywords if word.lower() not in keyword_song]
        querywords  = [word for word in querywords if word.lower() not in keyword_targetDomain]
        resultword = ' '.join(querywords)
        print(resultword)

    
    return select_type,  resultword


def top_most_text(search_term):

    with open('sinhala_songs_corpus/songs_meta_all.json') as f:
        meta_data = json.loads(f.read())

    artist_list = meta_data["artist_name_en"]
    genre_list = meta_data["genre_en"]
    music_list = meta_data["music_en"]
    lyricist_list = meta_data["lyricist_en"]
    targetDomain_list = meta_data["targetDomain_en"]

    documents_artist = [search_term]
    documents_artist.extend(artist_list)
    documents_genre = [search_term]
    documents_genre.extend(genre_list)
    documents_music = [search_term]
    documents_music.extend(music_list)
    documents_lyricist = [search_term]
    documents_lyricist.extend(lyricist_list)
    documents_targetDomain = [search_term]
    documents_targetDomain.extend(targetDomain_list)
    query = []
    select_type = False

    size = 100
    term_list = search_term.split()
    print(term_list)
    for i in term_list:
        if i.isnumeric():
            size = int(i)

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    other_select = False
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"artist_name_en": artist_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"genre_en": genre_list[i]}})
        select_type = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_targetDomain)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.TargetDomain":  targetDomain_list[i] 
                                }
                            }
                        } 
                    })
        select_type = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"music_en": music_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyricist)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"lyricist_en": lyricist_list[i]}})
        select_type = True
        other_select = True
    
    if select_type != True :
        query.append({"match_all" : {}})

    print(query)
    results = es.search(index='sinhala-songs',body={
        "size" : size,
        "query" :{
            "bool": {
                "must": query
            }
        },
        "sort" :{
            "views": {"order": "desc"}
        }
       ,
        "aggs": {
        "Metaphors": {
            "nested": {
                "path": "Metaphors"
            },
            "aggs": {
                "TargetDomain": {
                    "terms": {
                        "field": "Metaphors.TargetDomain.keyword",
                        "size": 20
                    },
                    
                },
                 "SourceDomain": {
                    "terms": {
                        "field": "Metaphors.SourceDomain.keyword",
                        "size": 20
                    },
                    
                }
            }
        }
        ,
         "genre": {
                "terms": {
                    "field": "genre.keyword",
                    "size" : 15    
                }        
            },
            "artist": {
                "terms": {
                    "field":"artist_name.keyword",
                    "size" : 15
                }             
            },
            "music": {
                "terms": {
                    "field":"music.keyword",
                    "size" : 15
                }             
            },
            "lyricist": {
                "terms": {
                    "field":"lyricist.keyword",
                    "size" : 15
                }             
            },    
    }
    })
    list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain = post_processing_text(results)
    return list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain

def top_most_filter_text(search_term, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter):

    with open('sinhala_songs_corpus/songs_meta_all.json') as f:
        meta_data = json.loads(f.read())

    artist_list = meta_data["artist_name_en"]
    genre_list = meta_data["genre_en"]
    music_list = meta_data["music_en"]
    lyricist_list = meta_data["lyricist_en"]
    targetDomain_list = meta_data["targetDomain_en"]

    documents_artist = [search_term]
    documents_artist.extend(artist_list)
    documents_genre = [search_term]
    documents_genre.extend(genre_list)
    documents_music = [search_term]
    documents_music.extend(music_list)
    documents_lyricist = [search_term]
    documents_lyricist.extend(lyricist_list)
    documents_targetDomain = [search_term]
    documents_targetDomain.extend(targetDomain_list)
    query = []
    select_type = False
    size = 100
    term_list = search_term.split()
    for i in term_list:
        if i.isnumeric():
            size = i

    if len(artist_filter) != 0 :
        for i in artist_filter :
            query.append({"match" : {"artist_name": i}})
    if len(genre_filter) != 0 :
        for i in genre_filter :
            query.append({"match" : {"genre": i}})
    if len(music_filter) != 0 :
        for i in music_filter :
            query.append({"match" : {"music": i}})
    if len(lyricist_filter) != 0 :
        for i in lyricist_filter :
            query.append({"match" : {"lyricist": i}})
    if len(targetDomain_filter) != 0 :
        print("p")
        for i in targetDomain_filter :
            query.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.TargetDomain":  i 
                                }
                            }
                        } 
                    })
    if len(sourceDomain_filter) != 0 :
        print("z")
        for i in sourceDomain_filter :
            query.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.SourceDomain":  i 
                                }
                            }
                        } 
                    })



    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    other_select = False
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"artist_name_en": artist_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"genre_en": genre_list[i]}})
        select_type = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_targetDomain)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({
                        "nested": {
                            "path": "Metaphors",
                            "query": {
                                "match": {                                    
                                    "Metaphors.TargetDomain":  targetDomain_list[i] 
                                }
                            }
                        } 
                    })
        select_type = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"music_en": music_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyricist)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"lyricist_en": lyricist_list[i]}})
        select_type = True
        other_select = True
    
    if select_type != True :
        query.append({"match_all" : {}})

    print(query)
    results = es.search(index='sinhala-songs',body={
        "size" : 500,
        "query" :{
            "bool": {
                "must": query
            }
        },
        "sort" :{
            "views": {"order": "desc"}
        },
       
        "aggs": {
        "Metaphors": {
            "nested": {
                "path": "Metaphors"
            },
            "aggs": {
                "TargetDomain": {
                    "terms": {
                        "field": "Metaphors.TargetDomain.keyword",
                        "size": 20
                    },
                    
                },
                 "SourceDomain": {
                    "terms": {
                        "field": "Metaphors.SourceDomain.keyword",
                        "size": 20
                    },
                    
                }
            }
        }
        ,
         "genre": {
                "terms": {
                    "field": "genre.keyword",
                    "size" : 15    
                }        
            },
            "artist": {
                "terms": {
                    "field":"artist_name.keyword",
                    "size" : 15
                }             
            },
            "music": {
                "terms": {
                    "field":"music.keyword",
                    "size" : 15
                }             
            },
            "lyricist": {
                "terms": {
                    "field":"lyricist.keyword",
                    "size" : 15
                }             
            },    
    }
    })
    list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain = post_processing_text(results)
    return list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain


def search_query(search_term):
    english_term = translate_to_english(search_term)
    select_type, strip_term = intent_classifier(english_term)  
    if select_type :
        list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain= top_most_text(strip_term)
    else :
        list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain = search_text(search_term)

    return list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain


def search_query_filtered(search_term, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter):
    english_term = translate_to_english(search_term)
    select_type, strip_term = intent_classifier(english_term)  
    if select_type :
        list_songs, artists, genres, music, lyricist,targetDomain ,sourceDomain = top_most_filter_text(strip_term, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter)
    else :
        list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain = search_filter_text(search_term, artist_filter, genre_filter, music_filter, lyricist_filter,targetDomain_filter,sourceDomain_filter)

    return list_songs, artists, genres, music, lyricist ,targetDomain ,sourceDomain
    
    
            







    
