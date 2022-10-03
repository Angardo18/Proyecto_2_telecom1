import socket



url = input("ingrese una URL: ").strip()

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
requestString+="Host:"+hostName+"\r\n\r\n"
print(requestString)
#inicial el socket
conect = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket tcp
#iniciar sesion tcp
conect.connect( (hostName, 80))
#enviar el request
conect.send(requestString.encode())
#recibir los datos
response = conect.recv(8192)
print(response.decode())

responseText = response.decode()
#Separar el contenido de de los datos 
headData = responseText.split('\r\n\r\n')
print(headData[1])
