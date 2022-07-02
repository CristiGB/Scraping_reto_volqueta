import re
import requests
import time
import lxml.html as html
from mercadoLibre_spider import visit_Anuncio
import pandas as pd

#una lista con los datos comparte la cualidades de busqueda 
List_data_search = ["Tipo","Kilómetro","Marca:","Modelo","Marca del motor", "Condición","Doble o Sencilla","Classificado", "Año","Transmisión"]
Ubicacion_v = []
Vendedor_v = []
Descripcion_v = []
TelSeller_v = []
for vect_data in List_data_search:
    globals()[vect_data+"_v"] = []



def extract_specs(item, parsed):
    try:
        Data = "UNKOWN"
        Xpath_data = '//*[contains(text(),"'+item+'")]/span/text()'

        #En el caso de encontrar si es doble o sencilla
        if item == "Doble o Sencilla":
            Tip_neumatic = False
            if len(parsed.xpath('////*[contains(text(),"Doble")]'))>=2:
               Tip_neumatic = "Doble"
            if parsed.xpath('////*[contains(text(),"sencilla")]'):
                if Tip_neumatic:
                    Tip_neumatic = Tip_neumatic+" and "+"sencilla"
                else:
                    Tip_neumatic = "sencilla"
            
            if Tip_neumatic:
                return Tip_neumatic


        if parsed.xpath(Xpath_data):
            Data = parsed.xpath(Xpath_data)[0]            
        if parsed.xpath(Xpath_data) and item == "Tipo":
           Data = ",".join(parsed.xpath(Xpath_data))
        return Data
        
    except ValueError as err:
        print(err)



def parse_vehiculos(link_home,link, browser, flag):
    try:

        full_link = link_home+link
        response = requests.get(full_link)
        if response.status_code == 200 or response.status_code == 418:
            browser.get(full_link)
            parsed = html.fromstring(browser.page_source)

            time.sleep(5)
            for item in List_data_search:
                Spec = extract_specs(item,parsed)
                globals()[item+"_v"].append(Spec)

            #Descripcion del vehiculo
            Xpath_descripcion = '//div[@class="containerDescription"]/center/text()'
            try:
                Descripcion_v.append(parsed.xpath(Xpath_descripcion)[0].replace("\n", " "))
            except:
                Descripcion_v.append("NONE")

            #Ubicacion del vehiculo
            ubicacion = extract_specs("Localização", parsed)
            print(ubicacion)
            Ubicacion_v.append(ubicacion)

            #Si ya se registro una volqueta con el mismo nombre duplicar telefono para envitar mas recalls          
            n_vendedor = extract_specs("Vendedor",parsed)
            print(n_vendedor)
            if n_vendedor in Vendedor_v :
                repeat_tel = TelSeller_v[Vendedor_v.index(n_vendedor)]
                if(repeat_tel != "NO FOUND" and repeat_tel.find('https://vehiculo.mercadolibre.com.co') == -1):
                    TelSeller_v.append(TelSeller_v[Vendedor_v.index(n_vendedor)])
                else:
                    TelSeller_v.append(visit_Anuncio(browser,flag))
            else: 
                TelSeller_v.append(visit_Anuncio(browser,flag))
            Vendedor_v.append(n_vendedor)
        else:
            raise ValueError(f'Error: {response.status_code}')

    except ValueError as err:
        print(err)


def create_dataframe():
    list_encabezado = List_data_search.copy()
    list_encabezado[2] = "Marca"
    list_encabezado[7] = "Precio"

    df = pd.DataFrame()
    for i in range(len(list_encabezado)):
        df[list_encabezado[i]] = globals()[List_data_search[i]+"_v"]
    
    df['Ubicacion'] = Ubicacion_v
    df['Vendedor'] = Vendedor_v
    df['Telefono del vendedor(Link)'] = TelSeller_v
    df['Descripcion'] = Descripcion_v

    return df

