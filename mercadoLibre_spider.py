import time, random
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import lxml.html as html


LINK_MERCADO = 'https://vehiculo.mercadolibre.com.co/'
a,b = 'áéíóúüñÁÉÍÓÚÜÑ','aeiouunAEIOUUN'
trans = str.maketrans(a,b)

##Visitar el anuncion original para obtener el telefono del vendedor
def visit_Anuncio(browser,flag):
    try:
        tel = "NO FOUND"
        parsed = html.fromstring(browser.page_source)
        Product_ID = parsed.xpath('//*[contains(text(),"Produto ID")]/span/text()')[0]
        Product_Title = parsed.xpath('//div[@class="conteudo"]/h1/text()')[0].strip()
        Product_Title = Product_Title.replace(",", "")
        Product_Title = Product_Title.translate(trans)
        Product_Title = Product_Title.replace(" ", "-")
        full_link_anuncio = LINK_MERCADO+"MCO-"+Product_ID+"-"+Product_Title+"-_JM"
        load = '//div[@class="andes-spinner__icon andes-spinner__icon--large"]'
        browser.get(full_link_anuncio)
        parsed = html.fromstring(browser.page_source)
        if requests.get(full_link_anuncio).status_code == 200 or requests.get(full_link_anuncio).status_code == 418:
            if flag == 0:
                browser.find_element(By.CSS_SELECTOR,'button.cookie-consent-banner-opt-out__action--key-accept').click()

            time.sleep(random.randint(3, 8))
            if len(parsed.xpath('//a[contains(text(),"teléfono") and @target="_self"]')) != 0:
                browser.find_element(By.XPATH,'//a[contains(text(),"teléfono") and @target="_self"]').click()
                time.sleep(random.randint(2, 5))
                parsed = html.fromstring(browser.page_source)
                time_load = 0
                while parsed.xpath(load) and  time_load < 30:
                    time_load =  time_load + 1
                    time.sleep(3)
                    parsed = html.fromstring(browser.page_source)
                if len(parsed.xpath('//*[@class="rc-anchor-container"]')) != 0: #mini catcha 
                        browser.find_element(By.CLASS_NAME,'rc-anchor-container').click()
                        time.sleep(10)
                        browser.find_element(By.XPATH,'//a[contains(text(),"teléfono") and @target="_self"]').click()
                        parsed = html.fromstring(browser.page_source)
                        while parsed.xpath(load):
                            time.sleep(3)
                            parsed = html.fromstring(browser.page_source)
                         
                time.sleep(3)
                if len(parsed.xpath('//div[@class="ui-seller-info__status-info__subtitle"]/ul/li')) != 0:
                    tel = browser.find_element(By.XPATH,'//div[@class="ui-seller-info__status-info__subtitle"]/ul/li')
                    tel = tel.text
                else:
                    tel = full_link_anuncio  
        return tel
    except ValueError as err:
        print(err)