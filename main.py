from telethon import TelegramClient, events, sync,Button
from telethon.events import NewMessage

from utils import createID,get_file_size,sizeof_fmt
from threads import ThreadAsync,Thread
from worker import async_worker

import asyncio
import base64
import zipfile
import os
import requests
import re
import config
import repouploader
import zipfile
import time
import animate

from repouploader import RepoUploader,RepoUploaderResult
import shorturl
import xdlink

tl_admin_users = ['darielxd','raydel0307'] #Poner aqui los user con acceso permanente
godlist = ['darielxd','raydel0307'] #Poner aqui los admin 

async def get_root(username):
    if os.path.isdir(config.ROOT_PATH+username)==False:
        os.mkdir(config.ROOT_PATH+username)
    return os.listdir(config.ROOT_PATH+username)

async def send_root(bot,ev,username):
    listdir = await get_root(username)
    reply = f'📄 {username}/ ({len(listdir)} archivos) 📄\n\n'
    i=-1
    for item in listdir:
        i+=1
        fname = item
        fsize = get_file_size(config.ROOT_PATH + username + '/' + item)
        prettyfsize = sizeof_fmt(fsize)
        reply += str(i) + ' - ' + fname + ' [' + prettyfsize + ']\n'
    await bot.send_message(ev.chat.id,reply)

def text_progres(index, max):
            try:
                if max < 1:
                    max += 1
                porcent = index / max
                porcent *= 100
                porcent = round(porcent)
                make_text = ''
                index_make = 1
                make_text += '\n'
                while (index_make < 21):
                    if porcent >= index_make * 5:
                        make_text += '▰'
                    else:
                        make_text += '▱'
                    index_make += 1
                make_text += ''
                return make_text
            except Exception as ex:
                return ''

def porcent(index, max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

async def download_progress(dl, filename, currentBits, totalBits, speed, totaltime, args):
    try:
        bot = args[0]
        ev = args[1]
        message = args[2]

        if True:
            msg = '========>>> Descargando <<<<========\n'
            msg += '⚜️ ' + filename + ' ⚜️ '
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '🌐 Descargando =>> ' + sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
            msg += '🌐 Velocidad  =>> ' + sizeof_fmt(speed) + '/s\n'
            msg += '🌐 Tiempo  =>> ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n'
            msg += '========>>> Descargando <<<<========\n\n'
            await bot.edit_message(ev.chat,message,text=msg)

    except Exception as ex:
        print(str(ex))


STORE_UPLOADER = {}
STORE_RESULT = {}
def upload_progress(filename, currentBits, totalBits, speed, totaltime, args):
    try:
        bot = args[0]
        ev = args[1]
        message = args[2]
        loop = args[3]

        if True:
            msg = '========>>> Subiendo <<<<========\n'
            msg += '⚜️ ' + filename + ' ⚜️ '
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '🌐 Subidos =>> ' + sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
            msg += '🌐 Speed =>> ' + sizeof_fmt(speed) + '/s\n'
            msg += '🌐 Tiempo =>> ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n'
            msg += '========>>> Subiendo <<<<========\n\n'
            STORE_UPLOADER[filename] = msg

    except Exception as ex:
        print(str(ex))

async def compress(bot,ev,text,message,username):
        await  bot.edit_message(ev.chat,message,'Comprimiendo...')
        text = str(text).replace('/rar ','')
        index = 0
        range = 0
        sizemb = 1900
        try:
            cmdtokens = str(text).split(' ')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
            if len(cmdtokens)>2:
                sizemb = int(cmdtokens[2])
        except:
            pass
        if index != None:
            listdir = await get_root(username)
            zipsplit = listdir[index].split('.')
            zipname = ''
            i=0
            for item in zipsplit:
                    if i>=len(zipsplit)-1:continue
                    zipname += item
                    print('zipname-item: ',zipname)
                    i+=1
            totalzipsize=0
            iindex = index
            while iindex<range:
                ffullpath = config.ROOT_PATH + username + '/' + listdir[index]
                totalzipsize+=get_file_size(ffullpath)
                iindex+=1
            zipname = config.ROOT_PATH + username + '/' + zipname
            print('zipname',zipname)
            multifile = zipfile.MultiFile(zipname,config.SPLIT_FILE)
            zip = zipfile.ZipFile(multifile, mode='w')
            while index<range:
                ffullpath = config.ROOT_PATH + username + '/' + listdir[index]
                await bot.edit_message(ev.chat,message,text=f'📚 {listdir[index]} 📚...')
                filezise = get_file_size(ffullpath)
                zip.write(ffullpath)
                index+=1
            zip.close()
            multifile.close()
            return multifile.files

async def onmessage(bot:TelegramClient,ev: NewMessage.Event,loop,ret=False):

    if ret:return

    proxies = None
    if config.PROXY:
        proxies = config.PROXY.as_dict_proxy()

    username = ev.message.chat.username
    text = ev.message.text

    #if username not in config.ACCES_USERS:
    if username not in tl_admin_users:
        await bot.send_message(ev.chat.id,'❌No tienes acceso comeverga, escribele a @darielxd ❌')
        return

    if not os.path.isdir(config.ROOT_PATH + username):
        os.mkdir(config.ROOT_PATH + username)

    try:
        if ev.message.file:
            message = await bot.send_message(ev.chat.id,'Analizando Solicitud...')
            filename = ev.message.file.id + ev.message.file.ext
            if ev.message.file.name:
                filename = ev.message.file.name
            filesave = open(config.ROOT_PATH + username + '/' + filename,'wb')
            chunk_por = 0
            chunkrandom = 100
            total = ev.message.file.size
            time_start = time.time()
            time_total = 0
            size_per_second = 0
            clock_start = time.time()
            async for chunk in bot.iter_download(ev.message,request_size = 1024):
                chunk_por += len(chunk)
                size_per_second+=len(chunk)
                tcurrent = time.time() - time_start
                time_total += tcurrent
                time_start = time.time()
                if time_total>=1:
                   clock_time = (total - chunk_por) / (size_per_second)
                   await download_progress(None,filename,chunk_por,total,size_per_second,clock_time,(bot,ev,message))
                   time_total = 0
                   size_per_second = 0
                filesave.write(chunk)
                pass
            filesave.close()
            await bot.delete_messages(ev.chat,message)
            #await send_root(bot,ev,username)
            return
            pass
    except Exception as ex:
        pass

    if '/start' in text:
        reply = '————————》<a href="https://t.me/darielxd">darielxd</a>《—————————\n'
        reply += 'Bot de darielxd\n\n'
        reply += 'Envia enlaces para descargar\n🔍 Enviame /info y leelo bien\n————————》<a href="https://t.me/darielxd">darielxd</a>《—————————\n'
        message = await bot.send_message(ev.chat.id,reply,parse_mode='html')
        pass
    if '/add' in text and username in godlist:
        usernameadd = text.split(' ')[1]
        tl_admin_users.append(usernameadd)
        print(tl_admin_users)
        db = config.space
        db[usernameadd] = 0
        message = await bot.send_message(ev.chat.id,'✅ El usario a sido añadido')
        return
    if '/proxy' in text and username in godlist:
        tx = str(text).split('/proxy ')[1]
        config.static_proxy = tx
        message = await bot.send_message(ev.chat.id,'✅ Has establecido el #Proxy: ' + config.static_proxy)
        return
    if '/del_proxy' in text:
        config.static_proxy = ''
        message = await bot.send_message(ev.chat.id,'❌ Global Proxy Desactivado ❌')
        return
    if '/cuota' in text and username in godlist:
        #global tl_admin_users
        uf = '𝕌𝕤𝕦𝕒𝕣𝕚𝕠𝕤 𝕡𝕖𝕣𝕞𝕚𝕥𝕚𝕕𝕠𝕤\n\n'
        print('EN LA DB')
        for usr in tl_admin_users:
            print('dbps: ',config.space[usr])
            if config.space[usr]>0:
                s = str(config.space[usr]).split('.')
                print(s)
                sp = s[0] + '.' + s[1][:2]
                print(sp)
            else:
                sp = str(config.space[usr])
                print(sp)
            uf+= '> @' + usr + ' > ' + str(sp) + ' mb\n'
        print(uf) 
        message = await bot.send_message(ev.chat.id,uf)
        return
    
    if '/ban' in text and username in godlist:
        usernamedell = text.split(' ')[1]
        tl_admin_users.remove(usernamedell)
        print(tl_admin_users)
        message = await bot.send_message(ev.chat.id,'❌ El usario a sido eliminado')
        return

    if '/info' in text:
        message = await bot.send_message(ev.chat.id,'⚠️ Cuando descargues los archivos tienes que renombrar el final haciendo lo siguiente\n\n>>>> Quitale el .rar  que tiene al final\n#Ejemplo:\nporno.7z.001.rar =>> porno.7z.001\n================\n\n>>>> Envia enlace directo y cuando suba usa /up el numero que le corresponde\n/up 0\n================\n')
        lag = os.path.basename('lag.tgs')
        message = await bot.send_file(ev.chat,lag)
        return
    if '/admin' in text:
        username = ev.message.chat.username
        print(username)
        txc = str(text).split('/admin ')
        t = '🙋‍♂️🗣 @' + username + '\n\n>> ' +  txc[1]
        print(t)
        message = await bot.send_message(1806431279,txc)
        message = await bot.send_message(ev.chat.id,'📡 Mensaje reportado a darielxd')
        return
    
    if '/get' in text and username in godlist:
        user = str(text).split('/get ')[1]
        await send_root(bot,ev,user)
        return
        
    if 'http' in text:
        message = await bot.send_message(ev.chat.id,'Analizis del enlace....espere unos segundos')
        dl = Downloader(config.ROOT_PATH + username + '/')
        file = await dl.download_url(text,progressfunc=download_progress,args=(bot,ev,message),proxies=proxies)
        if file:
            if file!='':
                await bot.delete_messages(ev.chat,message)
                await send_root(bot,ev,username)
            else:
                await bot.edit_message(ev.chat,message,text='💢Error De Enlace🔗')
        else:
             await bot.edit_message(ev.chat,message,text='💢Error De Enlace🔗')
        return

    if '/ls' in text:
        await send_root(bot,ev,username)
        return
    if '/rm' in text:
        message = await bot.send_message(ev.chat.id,'Iniciando ....')
        text = str(text).replace('/rm ','')
        index = 0
        range = 1
        try:
            cmdtokens = str(text).split(' ')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
        except:
            pass
        listdir = await get_root(username)
        while index < range:
              rmfile = config.ROOT_PATH + username + '/' + listdir[index]
              await bot.edit_message(ev.chat,message,text=f'🗑 {listdir[index]} 🗑...')
              os.unlink(rmfile)
              index += 1
        await bot.delete_messages(ev.chat,message)
        await send_root(bot,ev,username)
        return

    if '/rar' in text:
        message = await bot.send_message(ev.chat.id,'Analizando solicitud...')
        await compress(bot,ev,text,message,username)

    if '/up' in text:
        text = str(text).replace('/up ','')
        index = 0
        range = index+1
        txtname = ''
        try:
            cmdtokens = str(text).split('6034620666:AAGDRqwRmUenDP_EhdvlBpwA26Gqiy-t-Ls')
            if len(cmdtokens)>0:
                index = int(cmdtokens[0])
            range = index+1
            if len(cmdtokens)>1:
                range = int(cmdtokens[1])+1
            if len(cmdtokens)>2:
                txtname = cmdtokens[2]
        except:
            pass
        message = await bot.send_message(ev.chat.id,'Analizando Solicitud...')
        listdir = await compress(bot,ev,text,message,username)
        print('listdir: ',listdir)
        try:
            await bot.edit_message(ev.chat,message,text=f'🔑 Analizando solicitud de acceso')
            session:RepoUploader = await repouploader.create_session(config.PROXY)
            resultlist = []
            filesize = []
            txtsendname = str(listdir[0]).split('/')[-1].split('.')[0].split('_')[0] + '.txt'
            for fi in listdir:
                  dr = fi.split('/')
                  diir = dr[0] + '/' +dr[1]
                  trt = dr[2].split('.part')[1].replace('_.rar','')
                  if int(trt)>9:
                      ra = dr[2].replace('part','7z.0').replace('_.rar','.rar')
                  else:
                      ra = dr[2].replace('part','7z.00').replace('_.rar','.rar')
                  old_file = diir + '/' + dr[2]
                  new_file = diir + '/' + ra
                  ffname = str(fi).split('/')[-1]
                  cname = os.rename(old_file,new_file)
                  ffullpath = new_file
                  print('ffullpath: ',ffullpath)
                  ffname = str(new_file).split('/')[-1]
                  print('ffname: ',ffname)
                  fsize = get_file_size(ffullpath)
                  filesize.append(fsize)
                  if fsize>config.SPLIT_FILE:
                      await bot.edit_message(ev.chat,message,text=f'{ffname} Demasiado Grande, Debe Comprimir\nSe Cancelo La Subida')
                      return
                  await bot.edit_message(ev.chat,message,text=f'Subiendo ... {ffname}...')
                  result:RepoUploaderResult = find_all
                  def uploader_func():
                      result = session.upload_file(ffullpath,progress_func=upload_progress,progress_args=(bot,ev,message,loop))
                      STORE_UPLOADER[ffname] = result
                      if result:
                        STORE_RESULT[ffname] = result
                  tup = Thread(uploader_func)
                  tup.start()
                  try:
                      while True:
                          try:
                              msg = STORE_UPLOADER[ffname]
                              if msg is None:break
                              await bot.edit_message(ev.chat,message,msg)
                          except:pass
                          pass
                  except:pass
                  STORE_UPLOADER.pop(ffname)
                  try:
                      resultlist.append(STORE_RESULT[ffname])
                      STORE_RESULT.pop(ffname)
                  except:pass
                  index+=1
            if txtname!='':
                txtsendname = txtname
            txtfile = open(txtsendname,'w')
            urls = []
            for item in resultlist:
                urls.append(item.url)
            await bot.edit_message(ev.chat,message,text=f'⚒ Reparando Enlaces ⚒')
            txu = ''
            for ur in urls:
                txu+= str(ur) + '\n'
            txtfile.write(txu)
            txtfile.close()
            #data = xdlink.parse(urls)
            #if data:
            #    txtfile.write(data)
            #else:
            #    txtfile.write('Error al Escribir')
            #txtfile.close()
            tm = 0
            for x in filesize:
                tm+= x
            print('tamao: ',tm)
            spac = tm / 1000
            t = str(spac)
            inl = t[:1]
            fnl = t[1:3]
            space = str(inl) + '.' + str(fnl)
            tspace = config.space
            tspace[username] = tspace[username] + spac
            filesize = []
            txtinfo = '====>>> TERMINADO <<<<====\nNombre: ' + txtsendname + '\n\n>>>> ' + str(space) + 'mb en Partes de 99  mb\n====>>> Terminado <<<<===='
            username = ev.message.chat.username
            premium = os.path.basename('especial.tgs')
            await bot.delete_messages(ev.chat,message)
            await bot.send_file(ev.chat,txtsendname,
                                caption=f'{txtinfo}',
                                thumb='thumb.png',
                                buttons=[Button.url('>>>>>>> killerj00 <<<<<<<','https://t.me/killerj00')])
            await bot.send_file(ev.chat,premium)
            #await bot.send_file('-1001831303559',txtsendname,
                                #caption=f'{txtinfo}',
                                #thumb='thumb.png',
                                #buttons=[Button.url('@' +username,'https://t.me/' + username)])
            for fitem in listdir:
                try:
                    os.unlink(fitem)
                except Exception as ex:
                    print(str(ex))
                    pass
            os.unlink(txtsendname)
        except Exception as ex:
             await bot.send_message(ev.chat.id,str(ex))
    pass



def init():
    try:
        bot = TelegramClient(
            'bot', api_id=config.API_ID, api_hash=config.API_HASH).start(bot_token=config.BOT_TOKEN)

        print('Bot is Started!')

        try:
            loopevent = asyncio.get_runing_loop();
        except:
            try:
                loopevent = asyncio.get_event_loop();
            except:
                loopevent = asyncio.new_event_loop();

        @async_worker
        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
           await onmessage(bot,ev,loopevent)
          
        loopevent.run_forever()
    except Exception as ex:
        init()
        conf.procesing = False

if __name__ == '__main__': 
   init()
