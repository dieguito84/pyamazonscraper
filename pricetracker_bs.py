import re
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
        self._rating_full = html.find(id="averageCustomerReviews")    # get a wide section to refine the search later
        try:
            self._rating = self._rating_full.find(class_="a-icon-star").get_text()   # search refined - with value (there are reviews)
        except AttributeError:
            self._rating = None    # without value (there are not reviews)
        
        return self._rating
    
    def is_deal(self, html):
        '''
        Check if the product is a deal.
        '''
        if html.find(id="priceblock_dealprice"):
            return True
        else:
            return False
    
    def deal_expiry_time(self, html):
        '''
        Get time remaining for a deal.
        '''
        self._deal_expiry_time = html.find(id=re.compile("deal_expiry_time")).get_text()    # used re.compile to find a piece of string through regular expression

        return self._deal_expiry_time[13:]    # remove "Termina tra "
    

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
#page = pt.html("https://www.amazon.it/TESMED-elettrostimolatore-Muscolare-Power-potenziamento/dp/B0742H1F42")
#page = pt.html("https://www.amazon.it/HP-Monitor-Curvo-FreeSync-Argento/dp/B071LM1HYK/ref=gbps_tit_s-5_1669_17054278?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=ABY2DQ1E9WFMGKVZD0V8")
#page = pt.html("https://www.amazon.it/Tommy-Hilfiger-Maglietta-Captain-Medium/dp/B07L37J51Y/ref=sr_1_26?pf_rd_i=8805220031&pf_rd_m=A2VX19DFO3KCLO&pf_rd_p=c03a04c1-2325-4408-a172-1309a5cb832c&pf_rd_r=VR1FK5VEDV6FKB995GXC&pf_rd_s=merchandised-search-2&pf_rd_t=101&qid=1560727079&rw_html_to_wsrp=1&s=apparel&sr=1-26")
page = pt.html("https://www.amazon.it/KS801SE-QS-Seghetto-Alternativo-Autoselect-Pendolare/dp/B00VVFK5QC/ref=gbps_img_s-5_1669_361c1bd6?smid=A11IL2PNWYJU7H&pf_rd_p=55660c59-f0e0-412d-84b8-63a94ff41669&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A11IL2PNWYJU7H&pf_rd_r=7C21SMYBVDQ9EBNDJX9K")
print(pt.title(page))
print(pt.price(page))
print(pt.rating(page))
print(pt.is_deal(page))
if pt.is_deal(page) == True:
    print(pt.deal_expiry_time(page))