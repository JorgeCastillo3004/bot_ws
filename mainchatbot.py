from selenium import webdriver                                     # 
from selenium.webdriver.chrome.service import Service              # 
# from webdriver_manager.microsoft import EdgeChromiumDriverManager  # Importacion de controlador para navegador
from selenium.webdriver.common.by import By                        # 
from selenium.webdriver.common.keys import Keys                    # 
import re                                                          # "re" para expresiones regulares
import time                                                        # Time para generar tiempos de espera
import pandas as pd
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import chromedriver_autoinstaller 
chromedriver_autoinstaller.install() 

from funcChatbot import *
# from mainchatbot import *

def checkMensajes(usuario):    
    try:
        block = usuario.find_element(By.CLASS_NAME, '_2KKXC')
        numbmessages = block.find_element(By.CLASS_NAME, '_2H6nH')        
        
        messgepending = re.findall(r'\d+', numbmessages.text)
        if len(messgepending) != 0:            
            return True
    except:
        return False 

def getMsgPart(solicitud):    
    mensaje = solicitud.find_element(By.CLASS_NAME,"copyable-text").text
    html = solicitud.get_attribute('outerHTML')
    participante = re.findall(r'data-pre-plain-text=.{1}\[.+](.+?):', html)[0]    
    time = re.findall(r'\[(.+),\s{1}\d+\/\d+\/\d+]', html.replace('&nbsp;',''))[0]   
    date = re.findall(r'\d+\/\d+\/\d+', html)[0]
    return participante, mensaje, date, time
    return participante, mensaje, date, time

def extracDatos(usuariomsg):
    usuariomsg = usuariomsg.lower()    
    elements = usuariomsg.split()
    for r in elements:
        if '@' in r:
            correo = r
    usuariomsg = usuariomsg.replace(correo, '').replace('correo', '').replace('nombre', '')
    usuariomsg = re.sub(r'[^\w\s]', '', usuariomsg)

    usuariomsg = ' '.join(usuariomsg.split())
    return usuariomsg, correo

def answerUserRequest(intent, idcontexto, listadeopciones, respuesta, usuariomsg):
    poratender = True
    username, mail = '', ''
    ### INTEGRACION CON MODELO PREVIO ############
    if intent == 'saludos' and poratender:
        idcontexto = 1 
        poratender = False

    # Condicion para obligar a ingresar datos, de lo contrario no avanzara en el flujo de conversacion

    # BLOQUE PARA EL INGRESO DE DATOS POR PARTE DEL USUARIO
    if idcontexto == 1 and intent=='datos usuario' and poratender:
        username, mail = extracDatos(usuariomsg)
        respuesta ="""Confirme si sus datos son correctos,\n
                    Nombre: \n
                    {} \n
                    Correo: \n
                    {}
            """.format(username, mail)
        idcontexto = 2
        poratender = False
        
    if idcontexto == 1 and intent!='datos usuario' and poratender:        
        respuesta = "Para continuar es necesario el ingreso de tus datos"
        poratender = False
        
    if idcontexto == 2 and intent=='afirmativo' and poratender:
        respuesta = listadeopciones
        idcontexto = 3
        poratender = False

    if idcontexto == 2 and intent=='negativo' and poratender:
        respuesta = "Por favor ingrese de nuevo los datos en el formato indicado \n Nombre: Nombre Completo, Correo: ejemplocorreo@gmail.com "
        poratender = False
        
    # FINAL BLOQUE PARA EL INGRESO DE DATOS POR PARTE DEL USUARIO

    listoptions = ['opcion 1','opcion 2','opcion 3','opcion 4']

    # RESPUESTA EN EL CASO DE NO OBTENER NINGUNA OPCION VALIDA
    if idcontexto == 3 and intent not in listoptions and poratender:
        respuesta = "Debes ingresar una opción válida, como las mostradas anteriormente"
        poratender = False
        
    # FLUJO DE CONVERSACIONES PARA LA OPCION 1 #
    if idcontexto == 3 and intent == 'opcion 1' and poratender:
        linkguiadeusuario= 'https://drive.google.com/drive/u/3/folders/1TDzs215XTJnGzZP2Rs67gcoe8wJDhWxG'
        pregunta = '\n Confirme si con el uso de la guía de usuario logró solventar su problema\n ¿Si?'
        respuesta = """Primero ingrese a la guía de usuario y verifique las instrucciones detalladas en el manual """ + linkguiadeusuario + pregunta
        idcontexto = 10
        poratender = False

    # Vuelta al inicio de las opciones.
    if idcontexto == 10 and intent == 'afirmativo' and poratender:
        respuesta = """Espero haber sido de ayuda ¿Necesita realizar otra consulta?"""
        # Mostrar de nuevo las opciones disponibles
        idcontexto = 15
        poratender = False

    if idcontexto == 15 and intent == 'afirmativo' and poratender:
        respuesta = listadeopciones
        # Mostrar de nuevo las opciones disponibles
        idcontexto = 3
        poratender = False
        
    if idcontexto == 10 and intent == 'negativo' and poratender:
        respuesta = """Tomaremos sus datos y el equipo de soporte lo contactará a través de WhatsApp, en horario de oficina"""
        idcontexto = 12
        poratender = False
        
    # if idcontexto == 12 and intent == 'negativo' and poratender:
    #     respuesta = 
    #     idcontexto = 12
    #     poratender = False
    # FINAL DE FLUJO DE CONVERSACIONES PARA LA OPCION 1 #

    # FLUJO DE CONVERSACIONES PARA LA OPCION 2 #
    if idcontexto == 3 and intent == 'opcion 2' and poratender:                
        respuesta = """El equipo de soporte revisará, si aún no han sido añadidos sus cursos y luego se contactará a través de WhatsApp confirmando si el problema está solventado \n Espero haber sido de ayuda ¿Necesita realizar otra consulta?"""
        idcontexto = 20
        poratender = False

    if idcontexto == 20 and intent == 'afirmativo' and poratender:
        respuesta = listadeopciones
        # Mostrar de nuevo las opciones disponibles
        idcontexto = 3
        poratender = False

    if idcontexto == 20 and intent == 'negativo' and poratender:
        respuesta = "Gracias por contactar al equipo de FUNDESTEAM."
        # Mostrar de nuevo las opciones disponibles
        # idcontexto = 3
        poratender = False

    # FINAL FLUJO DE CONVERSACIONES PARA LA OPCION 2 #

    # FLUJO DE CONVERSACIONES PARA LA OPCION 3 #
    if idcontexto == 3 and intent == 'opcion 3' and poratender:                
        linkguiadeusuario= 'https://drive.google.com/file/d/1YPdlRBlNTX5XE2IO5lsY8wJBnIlj_De8/view?usp=sharing'
        pregunta = '\n Confirme si siguiendo las indicaciones de la guía de usuario logró solventar su problema'
        respuesta = """Primero ingrese a la guía de usuario y verifique las instrucciones detalladas en el manual """+linkguiadeusuario +pregunta
        idcontexto = 30
        poratender = False

    if idcontexto == 30 and intent == 'afirmativo' and poratender:
        respuesta = """Gracias por comunicar son el equipo de soporte, hasta luego"""                
        idcontexto = 0
        
    if idcontexto == 30 and intent == 'negativo' and poratender:
        respuesta = """Tomaremos sus datos y el equipo de soporte lo contactará a través de WhatsApp, en horario de oficina"""
        idcontexto = 0
        poratender = False
    # FINAL FLUJO DE CONVERSACIONES PARA LA OPCION 3 #

    # FLUJO DE CONVERSACIONES PARA LA OPCION 4 #
    if idcontexto == 3 and intent == 'opcion 4' and poratender:
        respuesta = "Pertenece a alguno de los siguientes colegios: \n"
        for iniciales in listadecolegios.keys():
            respuesta = respuesta + '{}:{}\n'.format(iniciales, listadecolegios[iniciales])                    
        respuesta = respuesta + "\n ¿Si?"
        idcontexto = 40
        poratender = False

    if idcontexto == 40 and intent == 'afirmativo' and poratender:
        respuesta = """Se recomienda contactar al colegio para la solicitud de contraseña"""
        idcontexto = 41
        poratender = False
        
    if idcontexto == 40 and intent == 'negativo' and poratender:
        respuesta = """Tomaremos sus datos y el equipo de soporte lo contactará a través de WhatsApp, en horario de oficina"""
        idcontexto = 42
        poratender = False
    # FINAL FLUJO DE CONVERSACIONES PARA LA OPCION 4 #

    # FLUJO DE CONVERSACIONES PARA LA OPCION 5 #
    if idcontexto == 3 and intent == 'opcion 5' and poratender:
        respuesta = "Por favor ingrese la fecha de compra, luego será contactado por el equipo de soporte vía whatsapp  \n"
        idcontexto = 50
        poratender = False

    if idcontexto == 50 and intent == 'afirmativo' and poratender:
        respuesta = "Gracias por comunicarse con FUNDESTEAM a la brevedad serás contactado a través de WhatsApp por equipo de soporte"
        poratender = False

    if idcontexto == 50 and intent == 'negativo' and poratender:
        respuesta = "Por favor ingrese la fecha de compra, en el siguiente formato dia/mes/año \n"
        idcontexto = 50
        poratender = False
    # FINAL DE FLUJO DE CONVERSACIONES PARA LA OPCION 5 #
    return respuesta, idcontexto, username, mail

def checkCurrentUsers(DictUsuarios, userphone):
    """ Check actual current users and update DictUsuarios"""
    listActiveUsers = DictUsuarios.keys()

    if userphone in listActiveUsers:

        idcontexto = DictUsuarios[userphone]['contexto']
        lastinteraction = DictUsuarios[userphone]['time']
        try:
            idoption = list(DictUsuarios[userphone]['opciones'].keys())[-1]
            idoption += 1
        except:
            idoption = 0

    else:
        DictUsuarios[userphone] = {}
        idoption = 0
        idcontexto = 0 

    return DictUsuarios, idoption, idcontexto

def getInsideConversation(conversacion):
    # conversacion = usuario.find_element(By.CLASS_NAME,"_8nE1Y") 
    conversacion.click()  # Se da click sobre la conversacion.
    time.sleep(3)

def getUserAnswer(driver):
    
    solicitudes = driver.find_elements(By.CLASS_NAME,"cm280p3y.to2l77zo.n1yiu2zv.c6f98ldp.ooty25bp.oq31bsqd")
    
    for solicitud in solicitudes[-4:]:  # Solo para tomar los ultimos 4 elementos.                
        userphone, mensaje, date, hora = getMsgPart(solicitud)                
        mensaje = mensaje.lower()

    return {"userphone":userphone, "mensaje":mensaje, "date":date, "hora":hora}

def saveUserData(userphone, username, mail, idcontexto, hora,  DictUsuarios):
    #  Save urer name and mail in DictUsuarios    
    if username!='' and mail !='':
        # ACTUALIZACION COMPLETA DEL DICCIONARIO DE DATOS
        DictUsuarios[userphone] = {"contexto":idcontexto, "username":username, "mail":mail,"hora":hora, "opciones":{} }    
    return DictUsuarios

def updateIntentionConsulted(userphone, intent, DictUsuarios, idoption):
    if intent == 'opcion 1' or intent == 'opcion 2' or intent == 'opcion 3' or intent == 'opcion 4':        
        DictUsuarios[userphone]["opciones"][idoption] = intent        
    return DictUsuarios
# usuariomsg =''
# i = 0
# DictUsuarios = {} # lista de usuarions en interaccion se tomara en cuenta un tiempo maximo de espera para reiciar el punto de la conversacion.
# variable de contexto, nodo de conversacion
# idcontexto = 0

def MainLoop(driver):
    
    global listadecolegios, listadeopciones
    DictUsuarios = {}
    idoption = 0
    filename = "User_atenddes.csv"

    if os.path.isfile(filename):
        df_users = pd.read_csv(filename)
    else:
        df_users = pd.DataFrame()

    usuariomsg = ''
    count = 0 

    while usuariomsg !='exit':        # Lazo infinito, solo se logra salir si la entra del usuario es "exit"
        time.sleep(3)
        print('#',DictUsuarios)    
        if count ==50:
            answer = input("Do you desire stop the bot? 'y' to stop or 'n' to continue running")
            if answer == 'y':
                usuariomsg = 'exit'
            count = 0
        count += 1
        poratender = True ##  Pending of atending

        # Busqueda de la clase "_10e6M", este bloque, incluye nombre del usuario, mensaje, verificador de mensajes.
        conversaciones = driver.find_elements(By.CLASS_NAME, "_8nE1Y")

        # dentro de cada conversacion vamos a realizar la busqueda del nombre del
        # usuario y la veridficacion de mensajes sin leer.
        for usuario in conversaciones:

            # A cada conversasion (Bloque) le llamamos usuario.            
            userphone = usuario.find_element(By.CLASS_NAME,"_21S-L").text # Busqueda del nombre del usuario.                            
            porresponder = checkMensajes(usuario) # Verificar si existen mensajes por leer

            # Condicion para entrar en cada conversacion (Solo entra si existen mensajes sin leer)
            if porresponder: # Si existen mensajes sin responder debemos dar click sobre la conversacion.

                # Verificacion si el usuario ya esta interactuando
                DictUsuarios, idoption, idcontexto = checkCurrentUsers(DictUsuarios, userphone)

                # Click in conversation
                getInsideConversation(usuario)

                # Buscar ultimos mensajes enviados por el usuario
                msgdata = getUserAnswer(driver)
                usuariomsg = msgdata['mensaje']
                # Sent message to model and return intent and answer
                respuesta, intent = chatbotRespuesta(msgdata['mensaje'])                

                # Check id context, intent and return the appropiate answer
                print("intent:", intent, "idcontexto:", idcontexto, "poratender:", poratender)                                
                respuesta, idcontexto, username, mail = answerUserRequest(intent, idcontexto, listadeopciones, respuesta, msgdata['mensaje'])

                # Buscar box text y enviar respuesta
                textRespuesta = driver.find_element(By.CLASS_NAME,"_3Uu1_") # busqueda del cuadro de texto para enviar respuesta
                textRespuesta.send_keys(respuesta)                  # Envio de mensaje.
                textRespuesta.send_keys(Keys.ENTER)                        # Envio de enter pare realizar envio.
                time.sleep(1)
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform() # generar ESC para salir de la conversacion

                DictUsuarios = saveUserData(userphone, username, mail, idcontexto, msgdata['hora'], DictUsuarios)
                DictUsuarios = updateIntentionConsulted(userphone, intent, DictUsuarios, idoption)

                DictUsuarios[userphone]["time"] = msgdata['hora']
                DictUsuarios[userphone]["contexto"] = idcontexto

                if intent == 'agradecimientos':
                    df = pd.DataFrame.from_dict(DictUsuarios[userphone])
                    print(DictUsuarios[userphone])                    
                    df_users = pd.concat([df_users, df])
                    DictUsuarios.pop(userphone)        

    df_users.to_csv(filename, index=False)
    return df

listadecolegios = {'CLP':'COLEGIO LOPEZ MENDEZ', 'CRC':'COLEGIO REPUBLICA DE CANADA','CFM':'COLEGIO FRANCISCO DE MIRANDA'}

listadeopciones = """A continuación ingrese  el número de la opción que más se ajuste a su motivo de consulta para agilizar el proceso de soporte.
                 \n 1 - No sé cómo acceder al STEAM VIRTUAL.
                 \n 2 - No veo mis cursos en el STEAM VIRTUAL.
                 \n 3 - Necesito asistencia para instalar el VRT. 
                 \n 4 - Olvidé la contraseña de acceso al STEAM VIRTUAL.
                 \n 5 - No he recibido el número de licencia del VRT."""


def __ini__():    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)


    # El metodo "get" navega a la pagina de la url suministrada.
    driver.get("https://web.whatsapp.com/")     # se debe escanear el codigo QR  y luego ejecutar la siquiente celda.
    answer = ''
    while answer!= 'y':
        answer = input("Confirm if the session is opened type 'y' ")

    MainLoop(driver)

__ini__()# bot_ws
