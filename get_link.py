from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.request
import requests

url = Request("https://ptgh.onego.ru/9006/")
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
f = open("ismen_nov.xls", "wb")
f.write(file_xls)
f.close()