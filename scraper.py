#Librerias
import os, time, random, requests
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ConectGoogleSheets import upload_sheet
from vehiculo_spider import parse_vehiculos, create_dataframe
import lxml.html as html



LINK_HOME = 'https://www.ocompra.com/'
LINK_COLOMBIA = LINK_HOME+'colombia'
DRIVER_PATH = './edgedriver/msedgedriver.exe' #tu direccion del path 
LINK_LOGIN_MERCADOLIBRE = 'https://www.mercadolibre.com/jms/mco/lgz/msl/login/'
XPATH_LINK_TO_ARTICLES = '//div[@class="containerDestaque"]//a[@class="colorTitulo"]/@href'
links_to_vehiculos = []



###Obtener los links de cada uno de los vehiculos que salen luego de buscar el producto deseado (volqueta)
def parse_links(link,browser):
    try:

        parsed = html.fromstring(link)
        links_pages = parsed.xpath(XPATH_LINK_TO_ARTICLES)
        for link in links_pages:
            links_to_vehiculos.append(link)

        time.sleep(5)
        XPATH_next = '//div[@class="containerPaginacao"]/nav/ul/*[last()]/a/@href'

        if parsed.xpath(XPATH_next): #se comprueba si hay mas paginas o si hemos lelgado al final

            full_next_link = LINK_HOME+parsed.xpath(XPATH_next)[0]
            response = requests.get(full_next_link)

            if response.status_code == 200 or response.status_code == 418:
                browser.get(full_next_link)
                parse_links(browser.page_source,browser)
            else:
             raise ValueError(f'Error: {response.status_code}')
        else:
            return

    except ValueError as err:
        print(err)


def login_mercadolibre(browser):
    try:
        response = requests.get(LINK_LOGIN_MERCADOLIBRE)
        time.sleep(random.randint(2,5))
        creden_merca = open('credential_mercadolibre.txt').readlines()
        if response.status_code == 200 and creden_merca:
            browser.get(LINK_LOGIN_MERCADOLIBRE)
            username = creden_merca[0]
            password = creden_merca[1]

            elementID = browser.find_element_by_id('user_id')
            elementID.send_keys(username)

            browser.find_elements_by_css_selector('button.andes-button.andes-button--large.andes-button--loud.andes-button--full-width').click()

            
            elementID = browser.find_element_by_id('password')
            elementID.send_keys(password)
            elementID.submit()

            browser.find_element_by_id('channel-sms').click()

    except ValueError as err:
        print(err)


###Funcion para aceder a la pagina principal 
def parse_home():
    try:
        browser = webdriver.Edge(DRIVER_PATH)
        #login_mercadolibre(browser)
        response = requests.get(LINK_COLOMBIA)
        browser.get(LINK_COLOMBIA)
        time.sleep(2)
        if response.status_code == 200 or response.status_code == 418:
            ElemetID_Search = browser.find_element(By.ID, 'textoBusca')
            ElemetID_Search.send_keys('volqueta')
            ElemetID_Search.send_keys(Keys.ENTER)
            time.sleep(5)
            
            parse_links(browser.page_source,browser)
            for i in range(len(links_to_vehiculos)):
                try:
                    print(i+1, " de ", len(links_to_vehiculos))
                    parse_vehiculos(LINK_HOME,links_to_vehiculos[i], browser,i)
                except ValueError as err:
                    print(err)
                    break

                
            
            df = create_dataframe()
            upload_sheet(df)
            browser.quit()

        else:
            raise ValueError(f'Error: {response.status_code}')

    except ValueError as err:
        print(err)



