from requests_html import HTMLSession

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

class PriceTracker():
    '''
    Amazon.it price tracker.
    '''

    def html(self, url):
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
    
    def offer(self, html):
        '''
        Check if the product is an offer
        '''
        pass


class Product():
    '''
    Basic product details.
    '''

    def __init_(self, url, title, price, rating, isoffer=False, offer_expiry_time=None):
        self.url = url
        self.title = title
        self.price = price
        self.rating = rating
        self.isoffer = isoffer
        self.offer_expiry_time = offer_expiry_time