import requests
from bs4 import BeautifulSoup

#URL = "https://www.amazon.it/dp/B01CPUGGIW"
URL = "https://www.amazon.it/gp/product/B01N2AYZBC"

page = requests.get(URL,headers={"User-Agent":"Defined"})
soup = BeautifulSoup(page.content, "html.parser")

title = soup.find(id="productTitle").get_text().strip()    # titolo

try:
    price = soup.find(id="priceblock_ourprice").get_text()   # prezzo normale
    offer = False
except AttributeError:
    price = soup.find(id="priceblock_dealprice").get_text()   # prezzo offerta
    offer = True

try:
    rating = soup.find(class_="a-icon-star").get_text()   # rating valorizzato (ci sono recensioni)
except AttributeError:
    rating = ""   # rating non valorizzato (non ci sono recensioni)

print(f"Il titolo dell'articolo è: {title}")
if offer:
    print(f"Il prezzo dell'articolo è: {price} e si tratta di un'offerta")
else:
    print(f"Il prezzo dell'articolo è: {price}")
if rating == "":
    print("Non ci sono recensioni")
else:
    print(f"La valutazione dell'articolo è: {rating}")