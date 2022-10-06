import socket

miDns = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


#mensaje dns

print(type("hola".encode()))

Id = 1234 
qr = 0 
opCode = 0
AA = 0
tc = 0
rd = 1
ra  = 0
z = 0
rcode = 0

parametros  = str(qr)
parametros += str(opCode).zfill(4)
parametros += str(AA) + str(tc) + str( rd)
parametros += str(ra) +str(z).zfill(3)
parametros += str(rcode).zfill(4)

query = "{:04x}".format(int(parametros,2))


QDCOUNT = 1 # Number of questions           4bit
ANCOUNT = 0 # Number of answers             4bit
NSCOUNT = 0 # Number of authority records   4bit
ARCOUNT = 0 # Number of additional records  4bit

message = ""
message += "{:04x}".format(ID)
message += query
message += "{:04x}".format(QDCOUNT)
message += "{:04x}".format(ANCOUNT)
message += "{:04x}".format(NSCOUNT)
message += "{:04x}".format(ARCOUNT)


  