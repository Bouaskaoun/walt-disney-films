from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

path = "https://en.wikipedia.org/wiki/Toy_Story_3"
content_html = requests.get(path).content
soup = bs(content_html, features="html.parser")
info_box = soup.find('table', class_='infobox vevent')
info_rows = info_box.find_all('tr')

def getInfo(row_data):
    if row_data.find('li'):
        return [li.get_text(" ", strip=True).replace('\xa0', ' ') for li in row_data.find_all('li')]
    else:
        return row_data.get_text(" ", strip=True).replace('\xa0', ' ')


movie_info = {}
for index, row in enumerate(info_rows):
    if index == 0:
        movie_info['title']= row.get_text(" ", strip=True)
    elif index == 1:
        continue
    else:
        key = row.find('th').get_text(" ", strip=True)
        value = getInfo(row.find('td'))
        movie_info[key]= value

pprint(movie_info)
