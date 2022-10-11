from interfaz import *
from PyQt5.QtWidgets import QWidget
import socket
import binascii

class Navegador(QWidget,Ui_Form):
    
    def __init__(self):
        
        super().__init__()
        self.setupUi(self)
        #-------- SLOTS -------------
        self.btnSearch.clicked.connect(self.buscar)
        self.btnRequest.clicked.connect(self.sendDns)
        
        
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
        
        response = conect.recv(4096)
        print(response.decode())
        responseText = ""
        while len(response) > 0:
            responseText += response.decode()
            response = conect.recv(4096)
        
        print(responseText)
        #Separar el contenido de de los datos 
        headData = responseText.split('\r\n\r\n')
        
        
        
        displayText = ""
        for i in range(1,len(headData)):
            displayText += headData[i]
            
        self.txtDisplay.setText(displayText)
    
    def sendDns(self):
        
        message = self.createDnsMessage(False)

        miDns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        miDns.sendto(binascii.unhexlify(message), (self.txtIpDns.text(),53))
        data, _ = miDns.recvfrom(8192)
        
        responseDns = binascii.hexlify(data).decode("utf-8")

        print(self.isTruncate(responseDns))
        
        sendTcp = self.isTruncate(responseDns)
        
        if sendTcp:
            #se arma el paquete, pero por tcp, indicando el largo del mensaje
            message = self.createDnsMessage(True)
            conect = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket tcp
            conect.connect( (self.txtIpDns.text(), 53))
            conect.send(binascii.unhexlify(message))
            response = conect.recv(8192)
            responseDns = binascii.hexlify(response).decode("utf-8")
        
        text = self.responseTreatment(responseDns,sendTcp)
        print(text)
        miDns.close()
        self.txtDnsResponse.setText(text)
    
    
    def isTruncate(self, data):
        
        responseParams = data[5:8] #parametros de la consulta
        params = "{:b}".format(int(responseParams,16)).zfill(16)
        TC = params[6]
        
        return TC == "1"    
    
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
    
    def getUrl(self,data,nextStart,isTcp):
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
                if isTcp:
                    offset+= 4 #debido a que si se recibe en TCP al inicio viene el largo,
                urlReturn, a = self.getUrl(data, offset,isTcp)
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
    def createDnsMessage(self,isTcp):
        Id = int(self.txtId.text())
        qr = 0      # query =0, response =1 1 bit
        opCode = 0  # Standard query        4 bits
        AA = 0      # ?
        tc = 0      #     
        rd = 1      #
        ra  = 0     #
        z = 0       #
        rcode = 0   #
        parametros  = str(qr)
        parametros += str(opCode).zfill(4)
        parametros += str(AA) + str(tc) + str( rd)
        parametros += str(ra) +str(z).zfill(3)
        parametros += str(rcode).zfill(4)
        query = "{:04x}".format(int(parametros,2))
        
        QDCOUNT = 1 # numero de preguntas          4bit
        ANCOUNT = 0 # numero de respuestas         4bit
        NSCOUNT = 0 # numero de RR autoritativos   4bit
        ARCOUNT = 0 # numero de RR adicionales     4bit

        message = ""
        message += "{:04x}".format(Id)      #hexadecimal 4 digitos (16 bits)
        message += query                    #hexadecimal 4 digitos (16 bits)
        message += "{:04x}".format(QDCOUNT) #hexadecimal 4 digitos (16 bits)
        message += "{:04x}".format(ANCOUNT) #hexadecimal 4 digitos (16 bits)
        message += "{:04x}".format(NSCOUNT) #hexadecimal 4 digitos (16 bits)
        message += "{:04x}".format(ARCOUNT) #hexadecimal 4 digitos (16 bits)

        addr = self.txtDomain.text()
        # Set de QNAME
        addrSplit = addr.split('.')
        for i in addrSplit:
            lenght = "{:02x}".format(len(i)) #largo de la etiqueta
            hexLabel = binascii.hexlify(i.encode()).decode() #caracteres hex, que representan el digito
            message += lenght
            message += hexLabel

        message += "00" #fin de la QNAME
        RRtype = self.txtRR.text()
        #QTYPE
        qtypeNum = self.getType(RRtype,True) #obtener el numero que representa el RR solicitado
        message += "{:04x}".format(qtypeNum) # se coloca en hex
        #QCLASS
        qclass = 1
        message += "{:04x}".format(qclass)
        
        if isTcp:
            print(len(message))
            lengthMessage = "{:04x}".format(int(len(message)/2)) #largo en bytes 
            message = lengthMessage + message

        return message
    
    def responseTreatment(self,responseDns,isTcp):
        responseText = ""
        if isTcp:
            #---------- header -----------------------
            responseId = responseDns[4:8] #ID de la consulta
            responseParams = responseDns[8:12] #parametros de la consulta
            questionCount = responseDns[12:16]
            answerCount = responseDns[16:20]
            nsCount = responseDns[20:24]
            aditionalCount = responseDns[24:28]
            parametros = "{:b}".format(int(responseParams,16)).zfill(16)
            #se convierte de string hex a entero
            nsCount = int(nsCount,16)
            answerCount = int(answerCount,16)
            aditionalCount = int(aditionalCount,16)
        else:
            #---------- header -----------------------
            responseId = responseDns[0:4] #ID de la consulta
            responseParams = responseDns[5:8] #parametros de la consulta
            questionCount = responseDns[9:12]
            answerCount = responseDns[13:16]
            nsCount = responseDns[17:20]
            aditionalCount = responseDns[20:24]
            parametros = "{:b}".format(int(responseParams,16)).zfill(16)
            #se convierte de string hex a entero
            nsCount = int(nsCount,16)
            answerCount = int(answerCount,16)
            aditionalCount = int(aditionalCount,16)
        #----- QUESTION SECTION ------------------
        nextStart = 24
        if isTcp:
            nextStart +=4
        
        url = ""
        url,nextStart = self.getUrl(responseDns, nextStart,isTcp)

        responseQtype = responseDns[nextStart:nextStart+4]
        nextStart+=4 #puntero a la siguiente parte de la respuesta a leer

        responseQtype = self.getType(int(responseQtype,16),False)
        responseQclass = responseDns[nextStart:nextStart+4]
        nextStart+=4 #puntero a la siguiente parte de la respuesta a leer
        # Answers section
        answerRR = []
        for i in range(0,answerCount+nsCount+aditionalCount):
            #print(nextStart)
            answerText = ""
            #obtener la informacion  
            answerName,nextStart = self.getUrl(responseDns, nextStart,isTcp)
            answerText += "NAME: "+ answerName

            answerType =  self.getType(int(responseDns[nextStart:nextStart+4],16), False) 
            AnswerClass = responseDns[nextStart+4:nextStart+8]
            answerTtl = int(responseDns[nextStart+8:nextStart+16],16)
            answerLength = int(responseDns[nextStart+16:nextStart+20],16)
            
            nextStart+=20
            answerText += " ,RR type: " + answerType
            if answerType == "A":
                answerText += ", IP: "
                #se busca la IP del dominio
                for i in range(0,4):
                    ipData = str(int(responseDns[nextStart:nextStart+2],16))
                    answerText += ipData
                    nextStart+=2
                    if(i!=3):
                        answerText += "."
            elif answerType == "NS":
                answerText += ", URL: "
                # se obtiene la url en ascii del ns RR
                nsUrl, nextStart = self.getUrl(responseDns, nextStart,isTcp)
                answerText += nsUrl
            elif answerType == "CNAME":
                answerText += ", URL: "
                nsUrl, nextStart = self.getUrl(responseDns, nextStart,isTcp)
                answerText += nsUrl
            else:
                nextStart+= 2*answerLength 
            #print(answerText)
            responseText+= answerText + '\n\n'
        
        return responseText

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Navegador()
    window.show()
    app.exec_()