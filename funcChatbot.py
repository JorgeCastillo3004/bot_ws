from tensorflow.keras.models import load_model
import json
import pickle
import numpy as np
import nltk
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer('spanish')
import random


def cleanEntrada(entradaUsuario):
    entradaUsuario = nltk.word_tokenize(entradaUsuario)
    entradaUsuario = [stemmer.stem(w.lower()) for w in entradaUsuario if w not in ignore_words]
    return entradaUsuario

def convVector(entradaUsuario, bolsadepalabras):
    
    entradaUsuario = cleanEntrada(entradaUsuario)
    
    vectorentrada = [0]*len(bolsadepalabras)    # colocar vector de entrada como ceros    
    for palabra in entradaUsuario:              # loop sobre la entrada del usuario
        
        if palabra in bolsadepalabras:          # verificación si la palabra esta dentro de la bolsa de palabras.
            
            indice = bolsadepalabras.index(palabra)    # obtanción del indice de la palabra actual, en la bolsa de palabras
            vectorentrada[indice] = 1                  #  asignación de 1 en el vector de entrada para el indice correspondiente.
            
    vectorentrada = np.array(vectorentrada)            #  conversión a un arreglo numpy
    return vectorentrada

def gettag(vectorentrada, LIMITE = 0):
    vectorsalida = model.predict(np.array([vectorentrada]))[0]

    # cargar los indices y los valores retornados por el modelo
    vectorsalida = [[i,r] for i,r in enumerate(vectorsalida) if r > LIMITE]    

    # ordenar salida en funcion de la probabilidad, valor que está contenido en el segundo termino de cada uno de sus elementos.
    vectorsalida.sort(key=lambda x: x[1], reverse=True)     
    
    listEtiquetas = []    
    for r in vectorsalida:   
        listEtiquetas.append({"intent": clases[r[0]], "probability": str(r[1])})   
    return listEtiquetas

def getResponse(listEtiquetas, biblioteca):
    etiqueta = listEtiquetas[0]['intent']

    listadediccionarios = biblioteca['intents']

    for dicionario in listadediccionarios:

        if etiqueta == dicionario['tag']:
            listaDeRespuestas = dicionario['responses']            
            respuesta = random.choice(listaDeRespuestas)
            break
    return respuesta

def chatbotRespuesta(entradaUsuario):
    vectorentrada = convVector(entradaUsuario, bolsadepalabras)
    listEtiquetas = gettag(vectorentrada, LIMITE = 0)
    respuesta = getResponse(listEtiquetas, biblioteca)
    return respuesta, listEtiquetas[0]['intent']

def checkMensajes(usuario):
    '''Funcion para verificar si existen mensajes por leer,
    en algunos casos la class=_1pJ9J, no se consigue,
    por eso se agrego la exception, y retorna verdadero (True) 
    si el bloque que se esta verificando tiene mensajes sin leer'''
    try:
        numMens = usuario.find_element(By.CLASS_NAME,"_1pJ9J").text                
        
        msleer = re.findall('\d+' ,numMens)        
        
        if len(msleer) != 0:
            pending = True
             
        else:
            # Usuarios silenciados, el simbolo posee el mismo nombre de la clase pero no contiene decimales
            pending = False
        
    except:        
        pending = False
    return pending

def getMsgPart(solicitud):    
    mensaje = solicitud.find_element(By.CLASS_NAME,"copyable-text").text# class="copyable-text"
    html = solicitud.get_attribute('outerHTML')#page_source
    participante = re.findall(r'data-pre-plain-text=.{1}\[.+](.+?):', html)[0]
    time =  solicitud.text    
    time = re.findall(r'data-pre-plain-text=.{1}\[(\d+\:\d+\.{3})', html) # (\d+\:\d+)
    date = re.findall(r'\d+\/\d+\/\d+', html)[0]
    return participante, mensaje, date, time


ignore_words = ["?","¿","!","¡","."]
model = load_model("modelo/chatbot_model.h5")
biblioteca = json.loads(open("files/intents.json").read())
bolsadepalabras = pickle.load(open("files/bolsadepalabras.pkl","rb"))
clases = pickle.load(open("files/classes.pkl","rb"))



