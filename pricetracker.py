from requests_html import HTMLSession

class PriceTracker():
    pass

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
    pass

    def __init_(self):
        pass