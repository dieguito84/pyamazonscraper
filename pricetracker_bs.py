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
        pass
    
    def title(self, html):
        '''
        Parser to find product's title.
        '''
        pass
    
    def price(self, html):
        '''
        Parser to find product's price.
        '''
        pass
    
    def rating(self, html):
        '''
        Parser to find product's rating.
        '''
        pass
    
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