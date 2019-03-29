import requests
from bs4 import BeautifulSoup

URL = "https://www.amazon.it/Telecamera-Sorveglianza-Bidirezionale-Infrarossi-Compatibile/dp/B00MA06JXU"
page = requests.get(URL,headers={"User-Agent":"Defined"})
soup = BeautifulSoup(page.content, "html.parser")
title = soup.find(id="productTitle").get_text().strip()
#price = soup.find(id="priceblock_ourprice").get_text()
price = soup.find(id="priceblock_dealprice").get_text()
rating = soup.find(class_="a-icon-star").get_text()
print(title)
print(price)
print(rating)