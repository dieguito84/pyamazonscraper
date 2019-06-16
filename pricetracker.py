from requests_html import HTMLSession

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

# TODO: use SQLite to store url to check, product details, users data for notifications
# TODO: think the entire application with Telegram Bot integration in mind
# TODO: add management of deal_expiry_time, probably with a different method than price()

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
        self._title = html.find("span[id=productTitle]", first=True).text
        
        return self._title
    
    def price(self, html):
        '''
        Parser to find product's price.
        '''
        try:
            self._price = html.find("span[id=priceblock_ourprice]", first=True).text
        except AttributeError:
            self._price = html.find("span[id=priceblock_dealprice]", first=True).text
        
        return self._price
    
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

pt = PriceTracker()
#page = pt.html("https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42")
page = pt.html("https://www.amazon.it/dp/B06XCF2JW1/ref=gbps_img_s-5_1669_ff19bcc3?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=XW61YXDK60Y35B4HF7CX")
#print(pt.title(page))
print(pt.price(page))