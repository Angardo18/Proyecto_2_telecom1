from interfaz import *
from PyQt5.QtWidgets import QWidget
import socket

class Navegador(QWidget,Ui_Form):
    
    def __init__(self):
        
        super().__init__()
        self.setupUi(self)
        #-------- SLOTS -------------
        self.btnSearch.clicked.connect(self.buscar)
        
        
    def buscar(self):
        url = self.txtUrl.text()
        #quitar espacios iniciales y finales
        url = url.strip()
        lista = url.split('/')
        # constantes
        hostName = ""
        requestString = "GET /"
        httpVersion = " HTTP/1.1\r\n"

        #ver si se ingreso https: o no
        initIndex = 0
        if lista[0].lower()=="http:":
            initIndex = 2

        hostName = lista[initIndex]
        for i in range(1+initIndex,len(lista)):
            if(i==1+initIndex):
                requestString +=  lista[i]
            else:
                requestString += '/' + lista[i]
        requestString+= httpVersion
        # se agregan los headers
        requestString+="Host: "+hostName+"\r\n"
        requestString+="Connection: keep-alive\r\n"
        requestString+="User-Agent: miNavegador\r\n"
        requestString+="Cache-Control: max-age:0\r\n\r\n"
        print(requestString)
        #inicial el socket
        conect = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket tcp
        #iniciar sesion tcp
        conect.connect( (hostName, 80))
        #enviar el request
        conect.send(requestString.encode())
        #recibir los datos
        response = conect.recv(2**33)
        print(response.decode())

        responseText = response.decode()
        #Separar el contenido de de los datos 
        headData = responseText.split('\r\n\r\n')
        
        self.txtDisplay.setText(headData[1])
    
    '''
    Devuelve el tipo del registro (RR), si inverse=False
    si inverse es True, entonces num debe ser un String con
    El tipo de registro y se retorna su valor de codigo segun
    el RFC 1034 y RFC 3596.
    '''
    def getType(self,num,inverse):    
        types = [
                "ERROR", # tipo 0 no existe
                "A","NS","MD","MF",
                "CNAME","SOA","MB",
                "MG","MR","NULL",
                "WKS","PTS","HINFO",
                "MINFO","MX","TXT",
                "","","","","","",
                "","","","","",
                "AAAA"]
        if inverse:
            return types.index(num)
        else:
            return types[num]
    
    '''  Obtener la url que se encuentra en los datos 
         Devueltos por el servidor DNS, data son los
         datos en donde se encuentra la url, y nexStart
         es el primer byte a leer de data
    '''
    
    def getUrl(data,nextStart):
        url = ""
        # se obtiene el numero de etiquetas, o bien el offset
        lenghtWord = int(data[nextStart:nextStart+2],16)
        actualChar = ''
        nextStart += 2
        while lenghtWord != 0:
            if lenghtWord <=63:
                #print("Lenght: ",lenghtWord)
                # si no se esta usando la compresion
                # se lee como una url normal
                for i in range(0,lenghtWord):
                    actualChar = chr(int(data[nextStart:nextStart+2],16))
                    #print(actualChar)
                    url += actualChar
                    nextStart +=2
            else:
                # si esta comprimido, se obtiene al byte al que apunta
                # y se llama a esta funcion de nuevo, pasandole como argumento
                # los mismos datos, y el byte donde comienza a leer, esto sucede
                # hasta que encuentre un 00 como largo de la etiqueta.
                offset = 2* (int(data[nextStart-2:nextStart+2],16) - int("C000",16))
                urlReturn, a = getUrl(data, offset)
                url += urlReturn
                nextStart+=2
                #print(nextStart)
                return url,nextStart
            # el sigueinte largo de etiqueta  
            lenghtWord = int(data[nextStart:nextStart+2],16)
            nextStart+=2
            # si no el la etiqueta de largo 0 se agrega un punto
            if lenghtWord != 0:
                url += "."
        return url,nextStart
    ''' Se crea el mensaje que sera enviado al DNS server'''
    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Navegador()
    window.show()
    app.exec_()