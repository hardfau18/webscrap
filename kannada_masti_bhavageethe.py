#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
import sys
import os
#get the link of song, requires beautifulsoup object

def get_link(page):
    songs = []
    song = page.find("div", class_="content")
    while True:
        try:
            Detail= BeautifulSoup(requests.get(song.a['href']).text, "lxml")    # get the song desc page
            song_link = Detail.find("div", class_="content")
            songs.append(song_link.a["href"])
            song = song.next_sibling
        except AttributeError:
            break
    return songs   
#checking if arguements are given

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} kannada_masti_album_link numbers_of_pages")
    sys.exit(1)

pages= int(sys.argv[2])
main_link = sys.argv[1]

song_count=0
#iterating over all pages and getting all song names
for i in range(pages):
    page = requests.get(main_link.replace("page=1",f"page={i+1}")).text
    page = BeautifulSoup(page, "lxml")
    #iterating over all songs
    for song in get_link(page):
        song_name = song.split("/")[7].rstrip("-mp3.html")
        song_link = song+"?download"
        print(f"songs:{song_count}")
        os.system(f"wget -q --show-progress -O {song_name}.mp3 {song_link}")
        song_count +=1

print("++++++++++++++++++++++++++++++all Done++++++++++++++++++++++++++++++++++")
