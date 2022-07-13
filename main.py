from bs4 import BeautifulSoup as bs
import requests
import json
from pprint import pprint

list_movies_path = "https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films"
list_movies_html = requests.get(list_movies_path).content
soup = bs(list_movies_html, features="html.parser")
movies = soup.select(".wikitable.sortable i a")


def clean_tags(soup):
    for tag in soup.find_all(["sup"]):
        tag.decompose()

def get_row_info(row_data):
    if row_data.find('li'):
        return [li.get_text(" ", strip=True).replace('\xa0', ' ') for li in row_data.find_all('li')]
    elif row_data.find('br'):
        return [text for text in row_data.stripped_strings]
    else:    
        return row_data.get_text(" ", strip=True).replace('\xa0', ' ')

def get_movie_info(relative_path):
    base_path = "https://en.wikipedia.org"
    path = base_path + relative_path
    movie_html = requests.get(path).content
    soup = bs(movie_html, features="html.parser")
    info_rows = []
    if soup.find('table', class_='infobox') != None:
        info_rows = soup.find('table', class_='infobox').find_all('tr')
    clean_tags(soup)
    movie_info = {}
    for index, row in enumerate(info_rows):
        if index == 0:
            movie_info['title']= row.get_text(" ", strip=True)
        elif index == 1:
            continue
        else:
            key = 'key'
            value = 'val'
            if row.find('th') != None:
                key = row.find('th').get_text(" ", strip=True)
            if row.find('td') != None:
                value = get_row_info(row.find('td'))
            if key != 'key':
                movie_info[key]= value
    return movie_info

#pprint(get_movie_info('/wiki/The_Great_Locomotive_Chase'))

list_movies_info = []
def fill_list_movies_info():
    for index, movie in enumerate(movies):
        if index % 10 == 0:
            print(index)
        try:
            relative_path = movie['href']
            list_movies_info.append(get_movie_info(relative_path))
            
        except Exception as e:
            print(movie.get_text())
            print(e)
    

fill_list_movies_info()

def save_data(title, data):
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(title):
    with open(title, encoding="utf-8") as f:
        return json.load(f)

save_data("disney_data.json", list_movies_info)

movie_info_list = load_data("disney_data.json")
