
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.request
import requests
import config

url = Request(config.DATASET_URL)
html_page = urlopen(url)

soup = BeautifulSoup(html_page, "html.parser")

link = []
for item in soup.findAll('a'):
    link.append(item.get('href'))

for index, elem in enumerate(link):
    if (elem.find('ismen_nov')) != -1:
        print(elem)
        break

file_xls = urllib.request.urlopen(elem).read()
f = open(config.ISMEN_FILE_NAME, "wb")
f.write(file_xls)
f.close()
