import re
import requests
from bs4 import BeautifulSoup

# url = "https://www.amazon.it/dp/B01CPUGGIW"    # prodotto normale (senza recensioni)
# url = "https://www.amazon.it/gp/product/B01N2AYZBC"    # prodotto con offerta (con recensioni)
url = "https://www.amazon.it/dp/B0764FT1HY"    # prodotto con offerta del giorno a tempo (con recensioni)

page = requests.get(url,headers={"User-Agent":"Defined"})
soup = BeautifulSoup(page.content, "html.parser")

title = soup.find(id="productTitle").get_text().strip()    # titolo

try:
    price = soup.find(id="priceblock_ourprice").get_text()   # prezzo normale
    offer = False
except AttributeError:
    price = soup.find(id="priceblock_dealprice").get_text()   # prezzo offerta
    offer = True
    try:
        deal_expiry_time = soup.find(id=re.compile("deal_expiry_time")).get_text()    # utilizzato re.compile per trovare un pezzo di stringa tramite regula expression
    except AttributeError:
        deal_expiry_time = ""    # deal_expiry_time non valorizzato (non è un'offerta a tempo)

try:
    rating = soup.find(class_="a-icon-star").get_text()   # rating valorizzato (ci sono recensioni)
except AttributeError:
    rating = ""   # rating non valorizzato (non ci sono recensioni)

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