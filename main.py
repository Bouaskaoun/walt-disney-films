from bs4 import BeautifulSoup as bs
import requests
import json
import re
from datetime import datetime
import pickle
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
    

#fill_list_movies_info()

def save_data(title, data):
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(title):
    with open(title, encoding="utf-8") as f:
        return json.load(f)

#save_data("disney_data.json", list_movies_info)

movie_info_list = load_data("disney_data.json")

def convert_running_time():
    def minutes_to_integer(running_time):
        if running_time == "N/A":
            return None
        
        if isinstance(running_time, list):
            return int(running_time[0].split(" ")[0])
        else:
            return int(running_time.split(" ")[0])

    for movie in movie_info_list:
        movie['Running time (int)'] = minutes_to_integer(movie.get('Running time', "N/A"))

convert_running_time()

def convert_budget_boxOffice():
    amounts = r"thousand|million|billion"
    number = r"\d+(,\d{3})*\.*\d*"

    word_re = rf"\${number}(-|\sto\s|–)?({number})?\s({amounts})"
    value_re = rf"\${number}"

    def word_to_value(word):
        value_dict = {"thousand": 1000, "million": 1000000, "billion": 1000000000}
        return value_dict[word]

    def parse_word_syntax(string):
        value_string = re.search(number, string).group()
        value = float(value_string.replace(",", ""))
        word = re.search(amounts, string, flags=re.I).group().lower()
        word_value = word_to_value(word)
        return value*word_value

    def parse_value_syntax(string):
        value_string = re.search(number, string).group()
        value = float(value_string.replace(",", ""))
        return value

    def money_conversion(money):
        if money == "N/A":
            return None

        if isinstance(money, list):
            money = money[0]
            
        word_syntax = re.search(word_re, money, flags=re.I)
        value_syntax = re.search(value_re, money)

        if word_syntax:
            return parse_word_syntax(word_syntax.group())

        elif value_syntax:
            return parse_value_syntax(value_syntax.group())

        else:
            return None

    for movie in movie_info_list:
        movie['Budget (float)'] = money_conversion(movie.get('Budget', "N/A"))
        movie['Box office (float)'] = money_conversion(movie.get('Box office', "N/A"))

convert_budget_boxOffice()

def convert_dates():
    def clean_date(date):
        return date.split("(")[0].strip()

    def date_conversion(date):
        if isinstance(date, list):
            date = date[0]
            
        if date == "N/A":
            return None
            
        date_str = clean_date(date)

        fmts = ["%B %d, %Y", "%d %B %Y"]
        for fmt in fmts:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                pass
        return None

    for movie in movie_info_list:
        movie['Release date (datetime)'] = date_conversion(movie.get('Release date', 'N/A'))

convert_dates()

def save_data_pickle(name, data):
    with open(name, 'wb') as f:
        pickle.dump(data, f)

def load_data_pickle(name):
    with open(name, 'rb') as f:
        return pickle.load(f)

save_data_pickle("disney_movie_data_cleaned.pickle", movie_info_list)

a = load_data_pickle("disney_movie_data_cleaned.pickle")
