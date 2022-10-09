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
                
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Navegador()
    window.show()
    app.exec_()