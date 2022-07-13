from bs4 import BeautifulSoup as bs
import requests
import json

list_movies_path = "https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films"
list_movies_html = requests.get(list_movies_path).content
soup = bs(list_movies_html, features="html.parser")
movie_detial = soup.find('table', class_='wikitable sortable').find_all('i')
movies_links = [movie.a['href'] for movie in movie_detial]

def get_row_info(row_data):
    if row_data.find('li'):
        return [li.get_text(" ", strip=True).replace('\xa0', ' ') for li in row_data.find_all('li')]
    else:
        return row_data.get_text(" ", strip=True).replace('\xa0', ' ')

def get_movie_info(relative_path):
    base_path = "https://en.wikipedia.org"
    path = base_path + relative_path
    movie_html = requests.get(path).content
    soup = bs(movie_html, features="html.parser")
    info_box = soup.find('table', class_='infobox vevent')
    info_rows = info_box.find_all('tr')
    movie_info = {}
    for index, row in enumerate(info_rows):
        if index == 0:
            movie_info['title']= row.get_text(" ", strip=True)
        elif index == 1:
            continue
        else:
            key = row.find('th').get_text(" ", strip=True)
            value = get_row_info(row.find('td'))
            movie_info[key]= value
    return movie_info

list_movies_info = []
def fill_list_movies_info():
    for movie_link in movies_links:
        list_movies_info.append(get_movie_info(movie_link))

#fill_list_movies_info()

def save_data(title, data):
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(title):
    with open(title, encoding="utf-8") as f:
        return json.load(f)

save_data("disney_data.json", list_movies_info)