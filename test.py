import requests
from bs4 import BeautifulSoup
import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

r = requests.get("https://www.nhs.uk/conditions/migraine/")
article1 = BeautifulSoup(r.content, 'html.parser')
article1 = article1.findAll("div", {"class": "article"})
article1 = article1[0]
article1 = article1.findAll("p")
print(article1)
print("\n\n\n")
#article1 = article1[0]


for i in range(len(article1)):
  print(article1[i].get_text())

