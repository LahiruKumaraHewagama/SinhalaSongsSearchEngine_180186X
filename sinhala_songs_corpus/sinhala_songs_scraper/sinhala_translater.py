import json
from googletrans import Translator
import re
import os

translator=Translator()

with open('song_output.json' , encoding='utf-8') as f:
  objects = json.load(f)

formatted_list= []
csv_list=[]


def generate_title_to_sinhala(title,title_sinhala):
  if(title_sinhala == None):
        tra=translator.translate (title.split('|')[1],dest='si').text
        return tra
  else:
        return title_sinhala

def generate_title_to_singlish(title):
  if(title == None):
    return None
  else:
    return title.strip().split('|')[0]

def convert_to_sinhala(text):
  text=text.strip()   
  if(len(text)==0):
    return " "
  else:
    tra=translator.translate(text,src="en",dest="si").text
    return tra

def convert_metaphors_to_sinhala(metaphors_list):
  # print(metaphors_list)
  metaphors=[]     
  if(len(metaphors_list)==0):
    return ""
  else:
    for meta in metaphors_list:
  
      metaphors.append({"Metaphor":meta['Metaphor'],"Meaning":translator.translate(meta['Meaning'],src="en",dest="si").text,"SourceDomain":translator.translate(meta['SourceDomain'],src="en",dest="si").text,"TargetDomain":translator.translate(meta['TargetDomain'],src="en",dest="si").text})
    return metaphors

def create_meta_all(formatted_list):

	dict_all_meta = {}
	list_keys = ['artist_name_en', 'genre_en', 'music_en', 'lyricist_en','sourceDomain_en','targetDomain_en']
	for i in list_keys :
		dict_all_meta[i] = []

	for items in formatted_list:
		for key in items:
			if key not in list_keys:
				if type(items[key]) == list:
					for val in items["Metaphors"]:          
						if translator.translate(val["SourceDomain"],src="si",dest="en").text not in dict_all_meta["sourceDomain_en"]:
							dict_all_meta["sourceDomain_en"].append(translator.translate(val["SourceDomain"],src="si",dest="en").text)    
						if translator.translate(val["TargetDomain"],src="si",dest="en").text not in dict_all_meta["targetDomain_en"]:
							dict_all_meta["targetDomain_en"].append(translator.translate(val["TargetDomain"],src="si",dest="en").text)  
			else:
				if items[key] not in dict_all_meta[key]:
					dict_all_meta[key].append(items[key])


	with open ('songs_meta_all.json','w+') as f:
		f.write(json.dumps(dict_all_meta))



def format_song(song,id):
  print(song['lyricist'])
  obj = {
    "id": id,
    "title_singlish" :  generate_title_to_singlish(song['title']),
    "title_sinhala" : generate_title_to_sinhala(song['title'],song['title_sinhala']),
    "artist_name" :  convert_to_sinhala(song['artist_name']),
    "artist_name_en" :  song['artist_name'],
    "genre" : convert_to_sinhala(song['genre']),
    "genre_en" : song['genre'],
    "lyricist" : convert_to_sinhala(song['lyricist']),
    "lyricist_en" : song['lyricist'],
    "music" : convert_to_sinhala(song['music']),
    "music_en" : song['music'],
    "views" : int(song['views'].replace(",","")),
    "lyrics" : song['song'].strip().replace("\r", ""),
    "Metaphors" : convert_metaphors_to_sinhala(song['Metaphors'])
  }
  return obj

def write_csv(csv_list):
  import csv

  header = ['id', 'title_singlish', 'title_sinhala', 'artist_name','artist_name_en', 'genre', 'genre_en', 'lyricist','lyricist_en', 'music', 'music_en','views','lyrics','Metaphors']
  data = csv_list

  with open('180186X_Songs_Corpus.csv', 'w', encoding='utf-8', newline='') as f:
      writer = csv.writer(f)

      # write the header
      writer.writerow(header)

      # write multiple rows
      writer.writerows(data)





c = 0
header = ['id', 'title_singlish', 'title_sinhala', 'artist_name','artist_name_en', 'genre', 'genre_en', 'lyricist','lyricist_en', 'music', 'music_en','views','lyrics','Metaphors']
  
for song in objects:
  c +=1  
  if(song['title'] == None ):
      c -=1 
      continue
  obj = format_song(song,c) 
  print(obj)
  formatted_list.append(obj)
  obj_list=[]
  for k in header:
    obj_list.append(str(obj[k]))
  csv_list.append(obj_list)
  print(obj_list)

with open('sinhala_song_lyrics.json' ,'w', encoding='utf-8') as outf:
  json.dump(formatted_list,outf,indent=4,ensure_ascii=False)

create_meta_all(formatted_list)
    
write_csv(csv_list)
