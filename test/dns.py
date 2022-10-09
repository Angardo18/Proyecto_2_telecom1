import socket
import binascii
from collections import OrderedDict

miDns = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#---------------------- Datos ingresados -----------------
# url a pedir
addr = "www.google.com"
RRtype = "A"
# url para los tipos de mensaje

# -------------------- funciones--------------------------
#RR types
def getType(num,inverse):    
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

#-------- crear el mensaje ---------------------------------------
def createDnsMessage():
    Id = 1234 
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

    # Set de QNAME
    addrSplit = addr.split('.')
    for i in addrSplit:
        lenght = "{:02x}".format(len(i)) #largo de la etiqueta
        hexLabel = binascii.hexlify(i.encode()).decode() #caracteres hex, que representan el digito
        message += lenght
        message += hexLabel

    message += "00" #fin de la QNAME

    #QTYPE
    qtypeNum = getType(RRtype,True) #obtener el numero que representa el RR solicitado
    message += "{:04x}".format(qtypeNum) # se coloca en hex
    #QCLASS
    qclass = 1
    message += "{:04x}".format(qclass)
    return message

def responseTreatment(responseDns):
    responseText = ""
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
    url = ""
    url,nextStart = getUrl(responseDns, nextStart)

    responseQtype = responseDns[nextStart:nextStart+4]
    nextStart+=4 #puntero a la siguiente parte de la respuesta a leer

    responseQtype = getType(int(responseQtype,16),False)# types[int(responseQtype,16)]
    responseQclass = responseDns[nextStart:nextStart+4]
    nextStart+=4 #puntero a la siguiente parte de la respuesta a leer
    # Answers section
    answerRR = []
    for i in range(0,answerCount+nsCount+aditionalCount):
        #print(nextStart)
        answerText = ""
        #obtener la informacion  
        answerName,nextStart = getUrl(responseDns, nextStart)
        answerText += "NAME: "+ answerName

        answerType =  getType(int(responseDns[nextStart:nextStart+4],16), False) 
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
            nsUrl, nextStart = getUrl(responseDns, nextStart)
            answerText += nsUrl
        else:
            nextStart+= 2*answerLength 
        #print(answerText)
        responseText+= answerText + '\n'
    
    return responseText
    
message = createDnsMessage()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(binascii.unhexlify(message), ("198.41.0.4",53))
data, _ = sock.recvfrom(4096)
responseDns = binascii.hexlify(data).decode("utf-8")

text = responseTreatment(responseDns)
print(text)


