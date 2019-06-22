import requests

from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

# test application performances and code needed to do same things using BeautifulSoup

class PriceTracker:
    '''
    Amazxon.it price tracker.
    '''

    def html(self, url, user_agent=USER_AGENT):
        '''
        Get HTML code for given URL.
        '''
        self.url = url
        self.user_agent = user_agent
        self.page = requests.get(self.url ,headers={"User-Agent": self.user_agent})
        self.soup = BeautifulSoup(self.page.content, "html.parser")

        return self.soup
    
    def title(self, html):
        '''
        Parser to find product's title.
        '''
        self._title = html.find(id="productTitle").get_text().strip()

        return self._title
    
    def price(self, html):
        '''
        Parser to find product's price.
        '''
        try:
            self._price = html.find(id="priceblock_ourprice").get_text()    # normal price
        except AttributeError:
            self._price = html.find(id="priceblock_dealprice").get_text()    # deal price
        
        return self._price
    
    def rating(self, html):
        '''
        Parser to find product's rating.
        '''
        try:
            self._rating = html.find(class_="a-icon-star").get_text()   # rating with value (there are reviews)
        except AttributeError:
            self._rating = None
        
        return self._rating
    
    def is_deal(self, html):
        '''
        Check if the product is a deal.
        '''
        pass
    
    def deal_expiry_time(self, html):
        '''
        Get time remaining for a deal.
        '''
        pass
    

class Product:
    '''
    Basic product details.
    '''

    def ___init___(self, url, title, price, rating, is_deal=False, offer_expiry_time=None):
        '''
        Object constructor.
        '''
        pass

pt = PriceTracker()
page = pt.html("https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42")
print(pt.title(page))
print(pt.price(page))
print(pt.rating(page))