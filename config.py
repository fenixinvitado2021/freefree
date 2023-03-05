import os
import ProxyCloud

BOT_TOKEN = '6034620666:AAGDRqwRmUenDP_EhdvlBpwA26Gqiy-t-Ls' #Aqui va el token del bot
API_ID =24253609#
API_HASH = '20c1618672d0d23844bf79d8a25de44f' #Tu api id de telegram
SPLIT_FILE = 1024 * 1024 * int(os.environ.get('split_file','99'))
ROOT_PATH = 'root/'
ACCES_USERS = os.environ.get('tl_admin_user','darielxd').split(';')

static_proxy = 'socks5h://KHDKKGYGJDJEGKYHJDGFGGYJIJIDRDGGLGGJKH' #agrega si kieres tener un proxy statico Con @raydel0307 si kieres comprar un proxy
PROXY = ProxyCloud.parse(static_proxy)

if PROXY:
  print(f'Proxy {PROXY.as_dict_proxy()}')
  
#Lo siguiente son las tablas de la base de datos de usarios, 
#es obligatorio agregar a aquellos usarios estaticos puestos en el main.py
#los agregados mediante /add no es necesario
#ponerlos valor 0 siempre

space = {'darielxd'}
space = {'Pjsr55'}
