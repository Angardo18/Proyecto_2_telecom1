import socket
import binascii

miDns = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# url a pedir
addr = "google.com"
RRtype = "A"
# url para los tipos de mensaje

#RR types
types = [
        "ERROR", # tipo 0 no existe
        "A",
        "NS",
        "MD",
        "MF",
        "CNAME",
        "SOA",
        "MB",
        "MG",
        "MR",
        "NULL",
        "WKS",
        "PTS",
        "HINFO",
        "MINFO",
        "MX",
        "TXT"
    ]

print(type("hola".encode()))

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


QDCOUNT = 1 # Number of questions           4bit
ANCOUNT = 0 # Number of answers             4bit
NSCOUNT = 0 # Number of authority records   4bit
ARCOUNT = 0 # Number of additional records  4bit

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
qtypeNum =  types.index(RRtype) # codigo del RR
message += "{:04x}".format(qtypeNum) # se coloca en hex
 
#QCLASS
qclass = 1

message += "{:04x}".format(qclass) 


print(message)

# UDP Message
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(binascii.unhexlify(message), ("198.41.0.4",53))
data, _ = sock.recvfrom(4096)
responseDns = binascii.hexlify(data).decode("utf-8")   
#print(h)

#descifrar la respuesta

responseId = responseDns[0:4]





  