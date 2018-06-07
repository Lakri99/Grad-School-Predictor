import requests
from bs4 import BeautifulSoup
import re
import csv

url = "https://yocket.in/applications-admits-rejects/arizona-state-university/2"

r = requests.get(url)
soup = BeautifulSoup(r.text)
print(soup)
