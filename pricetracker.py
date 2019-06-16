from requests_html import HTMLSession

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

# TODO: use SQLite to store url to check, product details, users data for notifications
# TODO: think the entire application with Telegram Bot integration in mind

class PriceTracker:
    '''
    Amazon.it price tracker.
    '''

    def html(self, url, user_agent=USER_AGENT):
        '''
        Get HTML code for given URL.
        '''
        self.url = url
        self.user_agent = user_agent
        self.session = HTMLSession()

        self.page = self.session.get(url, headers={"User-Agent": user_agent})
        self.page.html.render()

        return self.page.html
    
    def title(self, html):
        '''
        Parser to find product's title.
        '''
        return html.find("span[id=productTitle]", first=True).text
    
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


class Product:
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

#pt = PriceTracker()
#page = pt.html("https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42")

#print(pt.title(page))