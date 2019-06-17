import re

from requests_html import HTMLSession

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"

# TODO: evaluate the use of BeautifulSoup insteat of requests_html. Pro: is faster and is compatible with Python 3.5. Cons: do not support Javascript
# Do I really need Javascript in this specific task?
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
        self._ratingfull = html.find("div[id=averageCustomerReviews]", first=True)    # get a wide section to refine the search later
        try:
            #self._rating = html.find("div[id=averageCustomerReviews]", first=True).text
            #self._rating = html.find("i.a-icon-star", first=True).text
            self._rating = self._ratingfull.find("i.a-icon-star", first=True).text    # search refined
        except AttributeError:
            self._rating = None
        
        return self._rating
    
    def is_deal(self, html):
        '''
        Check if the product is an offer
        '''
        if html.find("span[id=priceblock_dealprice]", first=True):
            return True
        else:
            return False
    
    def deal_expiry_time(self, html):
        self._det_full = html.find("table[class=a-lineitem]", first=True)   # get a wide section to refine the search later 
        self._det_mid = self._det_full.find("td.a-span12")[2]    # get the third class="a-span12" found
        self._str = "deal_expiry_timer_"
        self._det_code = self._det_mid.html[self._det_mid.html.find(self._str) + len(self._str):self._det_mid.html.find(self._str) + len(self._str) + 8]    # find deal_expiry_time unique code using slicing (8 characters long)
        try:
            self._deal_expiry_time = html.find("span[id=" + self._str + self._det_code + "]", first=True).text[13:]
        except AttributeError:
            self._deal_expiry_time = None
        # TODO: probably AttributeError will never be raised since self._det_full.find("td.a-span12")[2] will be always with a value (wrong but present). Need to fix it.
        
        return self._deal_expiry_time


class Product:
    '''
    Basic product details.
    '''

    def __init_(self, url, title, price, rating, is_deal=False, offer_expiry_time=None):
        self.url = url
        self.title = title
        self.price = price
        self.rating = rating
        self.is_deal = is_deal
        self.offer_expiry_time = offer_expiry_time

pt = PriceTracker()
#page = pt.html("https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42")
page = pt.html("https://www.amazon.it/HP-Monitor-Curvo-FreeSync-Argento/dp/B071LM1HYK/ref=gbps_tit_s-5_1669_17054278?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=ABY2DQ1E9WFMGKVZD0V8")
#page = pt.html("https://www.amazon.it/Tommy-Hilfiger-Maglietta-Captain-Medium/dp/B07L37J51Y/ref=sr_1_26?pf_rd_i=8805220031&pf_rd_m=A2VX19DFO3KCLO&pf_rd_p=c03a04c1-2325-4408-a172-1309a5cb832c&pf_rd_r=VR1FK5VEDV6FKB995GXC&pf_rd_s=merchandised-search-2&pf_rd_t=101&qid=1560727079&rw_html_to_wsrp=1&s=apparel&sr=1-26")
print(pt.title(page))
print(pt.price(page))
print(pt.rating(page))
print(pt.is_deal(page))
if pt.is_deal(page) == True:
    print(pt.deal_expiry_time(page))