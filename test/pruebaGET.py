import socket

conect = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket tcp

#iniciar sesion tcp
conect.connect( ("gaia.cs.umass.edu", 80))

#enviar el request
conect.send(b"GET /search.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n")
#recibir los datos
response = conect.recv(10000000000)
#imprimir respuesta
print(response.decode())
conect.close()