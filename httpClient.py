import socket



url = input("ingrese una URL: ").strip()

lista = url.split('/')
# constantes
hostName = ""
requestString = "GET "
httpVersion = " HTTP/1.1\r\n"

#ver si se ingreso https: o mo
if(lista[0].lower()=="http:"):
    hostName = lista[2]
    for i in range(3,len(lista)):
        requestString += "/" + lista[i]
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
response = conect.recv(10000000000)
print(response.decode())
