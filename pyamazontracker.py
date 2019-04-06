import requests
from bs4 import BeautifulSoup

URL = "https://www.amazon.it/dp/B01CPUGGIW"
#URL = "https://www.amazon.it/gp/product/B01N2AYZBC"

page = requests.get(URL,headers={"User-Agent":"Defined"})
soup = BeautifulSoup(page.content, "html.parser")

title = soup.find(id="productTitle").get_text().strip()

try:
    price = soup.find(id="priceblock_ourprice").get_text()   # prezzo normale
except AttributeError:
    price = soup.find(id="priceblock_dealprice").get_text()   # prezzo offerta

try:
    rating = soup.find(class_="a-icon-star").get_text()   # rating valorizzato (ci sono recensioni)
except AttributeError:
    rating = "Non ci sono recensioni"   # rating non valorizzato (non ci sono recensioni)

print(title)
print(price)
print(rating)