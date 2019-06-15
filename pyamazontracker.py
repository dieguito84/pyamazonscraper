import re
import requests
from bs4 import BeautifulSoup

# URL FOR DEBUG
# url = "https://www.amazon.it/dp/B01CPUGGIW"    # normal product (without reviews)
# url = "https://www.amazon.it/gp/product/B01N2AYZBC"    # product in offer (with reviews)
url = "https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42"    # product with timed daily offer (with reviews)

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"

page = requests.get(url,headers={"User-Agent": user_agent})
soup = BeautifulSoup(page.content, "html.parser")

title = soup.find(id="productTitle").get_text().strip()    # title

try:
    price = soup.find(id="priceblock_ourprice").get_text()   # normal price
    offer = False
except AttributeError:
    price = soup.find(id="priceblock_dealprice").get_text()   # offer price
    offer = True
    try:
        deal_expiry_time = soup.find(id=re.compile("deal_expiry_time")).get_text()    # used re.compile to find a piece of string through regular expression
    except AttributeError:
        deal_expiry_time = ""    # deal_expiry_time without value (it's not a timed offer)

try:
    rating = soup.find(class_="a-icon-star").get_text()   # rating with value (there are reviews)
except AttributeError:
    rating = ""   # rating without value (there are not reviews)

print(f"Il titolo dell'articolo è {title}")
if offer:
    if deal_expiry_time != "":
        print(f"Il prezzo dell'articolo è {price} e si tratta di un'offerta che termina tra {deal_expiry_time[13:]}")

    else:
        print(f"Il prezzo dell'articolo è {price} e si tratta di un'offerta")
else:
    print(f"Il prezzo dell'articolo è {price}")
if rating == "":
    print("Non ci sono recensioni")
else:
    print(f"La valutazione dell'articolo è {rating}")