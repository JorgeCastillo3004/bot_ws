import json

import pickle
import numpy as np

import nltk

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense,Dropout
from tensorflow.keras.optimizers import SGD

from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer('spanish')

def CreateBagWords(biblioteca, bolsadepalabras, ignore_words):
	for intent in biblioteca['intents']:
	    
	    clases.append(intent['tag'])
	    
	    for pattern in intent['patterns']:       
	        result = nltk.word_tokenize(pattern)        
	        bolsadepalabras.extend(result)
	        
	        documents.append((result, intent['tag']))

	bolsadepalabras = [stemmer.stem(w.lower()) for w in bolsadepalabras if w not in ignore_words]
	pickle.dump(bolsadepalabras, open("files/bolsadepalabras.pkl","wb")) # guarda bolsa de palabras como archivo .pkl
	pickle.dump(clases, open("files/classes.pkl","wb"))  

	return bolsadepalabras, clases, documents

def cleanString(words, ignore_words):
    '''Funcion utilizada para limpiar lista de palabras,
     el uso de funciones, evita repetir las palabras innecesarias de codigo'''
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    return words

def trainSet(documents, ignore_words):
	training = [] # Creacion de lista vacia de para agregar los vectores construidos en las siguientes lineas.

	for doc in documents:
	    
	    interaccion = doc[0]            # obtencion del primer elemento guardado en cada posicion de la lista documents.
	    interaccion = cleanString(interaccion, ignore_words) # limpieza del strin "interaccion"
	    
	    entradacodificada = []  # creacion de la lista vacia llamada "entradacodificada"
	    
	    # codificacion de la entrada
	    for palabra in bolsadepalabras:
	        if palabra in interaccion:
	            entradacodificada.append(1)
	        else:
	            entradacodificada.append(0)    
	    
	    # codificacion de la etiqueta
	    salidacodificada = [0]*len(clases)
	    indice = clases.index(doc[1])
	    salidacodificada[indice] = 1
	    
	    training.append([entradacodificada, salidacodificada])
	    
	training = np.array(training, dtype=list)

	x_train = list(training[:,0])

	y_train = list(training[:,1])

	return x_train, y_train

ignore_words = ["?","¿","!","¡","."] # Lista de simbolos que se desean eliminar.
biblioteca = open('files/intents.json')
biblioteca = json.load(biblioteca)

bolsadepalabras = [] # creación de lista vacia para guardar palabras
clases = []          # creacion de lista para guardar etiquetas de la conversación
documents = []       # creación de lista para guardar entrada y su correspondiente etiqueta.

bolsadepalabras, clases, documents = CreateBagWords(biblioteca,
					 bolsadepalabras, ignore_words)

# bolsadepalabras = cleanString(bolsadepalabras, ignore_words)
pickle.dump(bolsadepalabras,open("files/bolsadepalabras.pkl","wb")) # guarda bolsa de palabras como archivo .pkl
# pickle.dump(clases,open("classes.pkl","wb"))        # guarda lista de clases como archivo .pkl

x_train, y_train = trainSet(documents, ignore_words)


# CREATE AND TRAIN MODEL.
model = Sequential()

model.add(Dense(128, input_shape=(len(x_train[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64,activation='relu')) #capa oculta -> aprendizaje
model.add(Dropout(0.5))
model.add(Dense(len(y_train[0]), activation='softmax'))


sgd = SGD(learning_rate=0.01,momentum=0.9,nesterov=True) # ,decay=1e-6

model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

hist = model.fit(np.array(x_train),np.array(y_train),epochs=300,batch_size=5,verbose=True)
model.save("modelo/chatbot_model.h5",hist)
print("MODELO CREADO")
print(bolsadepalabras)