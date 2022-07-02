import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
spreadsheet_name = "Scraping_BaseDatos_Volquetas"

credenciales = ServiceAccountCredentials.from_json_keyfile_name("credentials.json",scope)#Nos ayuda a leer el archivo json
client = gspread.authorize(credenciales)

try: 
    client.open(spreadsheet_name)
except:
    spreadsheet = client.create(spreadsheet_name)
    spreadsheet.share("isa.gomez.ba08@gmail.com", perm_type='user', role='writer')#compartir de cuanta cleinte a la personal

sheet = client.open(spreadsheet_name).sheet1

def upload_sheet(df):
    #primero el encabezado y luego los datos
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
