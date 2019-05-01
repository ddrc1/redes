import socket
import sys
import ssl
import errno
import re
import base64
from email.header import decode_header
import os as OS
from textExtracter import TextExtracter

CR = b'\r'
LF = b'\n'
CRLF = CR+LF

_MAXIMAL_LINE_LENGTH = 2048

__all__ = ["ClientPOP3_SSL","error_exp"]

class error_exp(Exception): pass


class ClientPOP3_SSL:

    def __init__(self, host, porta):
        self.host = "pop.gmail.com"
        self.port = 995
        self.encoding = 'UTF-8'
        self.context = ssl._create_stdlib_context(certfile=None, keyfile=None)
        self.socket_init = self.createConnectionSocket()
        self.file = self.socket_init.makefile('rb')

    def createConnectionSocket(self):
        sock = socket.create_connection((self.host, self.port), socket._GLOBAL_DEFAULT_TIMEOUT)
        return self.context.wrap_socket(sock, server_hostname=self.host)
        
    def user(self, user):
        return self.command('USER %s' % user)

    def pass_(self, password):
        return self.command('PASS %s' % password)

    def command(self, line):
        line = bytes(line, self.encoding)
        self.socket_init.sendall(line + CRLF)
        return self.getResponse()
    
    def stat(self):
        responseCommand = self.command('STAT')
        resp_split = responseCommand.split()
        amountMessages = int(resp_split[1])
        sizeMessages = int(resp_split[2])
        return (amountMessages, sizeMessages)

    def retr(self, option=None):
        line = 'RETR %s' % option
        line = bytes(line, self.encoding)
        self.socket_init.sendall(line + CRLF)
        return self.getResponseLong()

    def list(self, option=None):
        if option is None:
            line = bytes('LIST', self.encoding)
            self.socket_init.sendall(line + CRLF)
            return self.getResponseLong()
        return self.command('LIST %s' % option)

    def dele(self, option):
        return self.command('DELE %s' % option)

    def rpop(self, user):
        return self.command('RPOP %s' % user)

    def noop(self):
        return self.command('NOOP')

    def rset(self):
        return self.command('RSET')

    def getResponse(self):
        (resp, octets) = self.getLine()
        if not resp.startswith(b'+'):
            raise error_exp(resp)
        return resp

    def getLine(self):
        line = self.file.readline(_MAXIMAL_LINE_LENGTH + 1)
        if len(line) > _MAXIMAL_LINE_LENGTH:
            raise error_exp('exception length line !')

        if not line: raise error_exp('End of File(EOF)')
        octets = len(line)
        if line[-2:] == CRLF:
            return line[:-2], octets
        if line[:1] == CR:
            return line[1:-1], octets
        return line[:-1], octets
    
    def getResponseLong(self):
        resp = self.getResponse()
        list = []; octets = 0
        line, o = self.getLine()
        while line != b'.':
            if line.startswith(b'..'):
                o = o-1
                line = line[1:]
            octets = octets + o
            list.append(line)
            line, o = self.getLine()
        return resp, list, octets

    def quit(self):
        resp = self.command('QUIT')
        self.close()
        return resp
    
    def close(self):
        try:
            file = self.file
            self.file = None
            if file is not None:
                file.close()
        finally:
            sock = self.socket_init
            self.socket_init = None
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError as exc:
                    if (exc.errno != errno.ENOTCONN
                       and getattr(exc, 'winerror', 0) != 10022):
                        raise
                finally:
                    sock.close()


if __name__ == "__main__":

    email = "jose.victor@edu.unifor.br"
    senha = "15683479"
    
    pop3 = ClientPOP3_SSL("pop.gmail.com", 995)
    textDecode = TextExtracter()

    print(pop3.getResponse().decode('UTF-8'))
    
    pop3.user(email)
    pop3.pass_(senha)
    
    (numMsgs, totalSize) = pop3.stat()
    
    numMSG = 3

    (resp, l, octets) = pop3.retr(numMSG)

    print(resp.decode('UTF-8'))
    
    fileNumMensagem = str(numMSG) + ".txt"

    fileMensage = open(fileNumMensagem, "w+")

    for i in l:
        i = i.decode('ISO-8859-1')
        fileMensage.write(i + "\n")
    
    fileMensage.close()

    fileMensageRead = open((str(numMSG) + ".txt"), "r")
    
    file_read = fileMensageRead

    subject = ""
    received = False
    dataRecebida = ""
    arquivos = []
    deliveredTo = ""
    dataEnvio = ""
    armazenarBase64 = False
    nameFrom = ""
    emailFrom = ""
    indiceArquivo = -1
    removeFile = False
    conteudo = ""
    flagConteudo = -1
    removeFileConteudo = False
    quebraLinha = False
    
    for read in file_read:
        if(read != "\n" and read != "\r" and read != "" and read != " "):
            if(received == True) and (not dataRecebida):
                dataRecebida = read.strip()
            if(read.split(":")[0] == "Content-ID") and (armazenarBase64 == True):
                armazenarBase64 = False
            if (len(read) > 2):
                if(read[0] == "-" and read[1] == "-"):
                    if(armazenarBase64 == True):
                        armazenarBase64 = False
                        removeFile = False
                    if(flagConteudo == 0):
                        flagConteudo += 1
            if (flagConteudo == 0):
                nameFileConteudo = (str(numMSG) + str("_conteudo_.txt"))
                strLine = ""
                textDecode.feed(read)
                read = textDecode.getValue()
                if(quebraLinha == True):
                    strLine = "\n"
                    quebraLinha = False
                if(removeFileConteudo == False):
                    if(OS.path.exists(nameFileConteudo)):
                        OS.remove(nameFileConteudo)
                        removeFileConteudo = True
                        quebraLinha = True
                with open(nameFileConteudo, "a+") as file_writeConteudo:
                    if(read[len(read) - 2] == "="):
                        read = read[:len(read)-2]
                        read += "\n"
                        strLine = ""
                    if quebraLinha == True:
                        file_writeConteudo.write((read + strLine))
                    else:
                        file_writeConteudo.write((strLine + read + strLine))
            if(armazenarBase64 == True):
                if(indiceArquivo >= 0):
                    nameFileBase64 = (str(arquivos[indiceArquivo]) + str("_base64_.txt"))
                    if(removeFile == False):
                        if(OS.path.exists(nameFileBase64)):
                            OS.remove(nameFileBase64)
                            removeFile = True
                    with open(nameFileBase64, "a+") as file_writeBase64:
                        file_writeBase64.write(read)
            if(read.split(":")[0] == "Content-Type"):
                fileName = read.split(";")[1].split("\"")
                if(fileName[0].strip() == "name="):
                    for part in decode_header(fileName[1].strip()):
                        (name, code) = part
                        if(code != None):
                            name = name.decode(code)
                    fileName[1] = name
                    arquivos.append(fileName[1].replace("\n",""))
                    indiceArquivo += 1
            if(read.split(":")[0] == "Content-Transfer-Encoding"):
                if(read.split(":")[1].strip() == "quoted-printable"):
                    if(flagConteudo == -1):
                        flagConteudo = 0
            if(read.split(":")[0] == "X-Attachment-Id"):#base64
                if indiceArquivo > -1:
                    armazenarBase64 = True
            if(read.split(":")[0] == "Received"):#data recebida
                received = True
            if(read.split(":")[0] == "Date"):#data de envio
                dataEnvio = read.split(":")[1]
            if(read.split(":")[0] == "Thread-Topic"):#assunto
                subject = read.split(":")[1]
            if(read.split(":")[0] == "Subject") and (subject == ""):#assunto
                for part in decode_header(read.split(":")[1]):
                    (subjectName, code) = part
                    if(code != None):
                        subjectName = subjectName.decode(code)
                if(subjectName.split(":")[0] == "Fwd"):
                    subjectName = subjectName[5:]
                subject = subjectName
            if(read.split(":")[0] == "Delivered-To"):#destinatario
                deliveredTo = read.split(":")[1]
            if(read.strip() == "Content-Transfer-Encoding: base64"):
                if indiceArquivo > -1:
                    armazenarBase64 = True
            if(read.split(":")[0] == "From"):#remetente
                fromEmail = read.split(":")[1].split("<")
                emailFrom = fromEmail[1][0:(len(fromEmail[1]) - 2)]
                for part in decode_header(fromEmail[0].strip()):
                    (name, code) = part
                    if(code != None):
                        name = name.decode(code)
                nameFrom = name
        else:
            if(flagConteudo == 0):
                quebraLinha = True
    fileMensageRead.close()
    print("Numero de mensagens:\t", numMsgs)
    print("\n------------------------------\n")
    print("Assunto:\t", subject.strip())
    print("Data Recebida:\t", dataRecebida.strip())
    print("Data de Envio:\t", dataEnvio.strip())
    print("Remetente:\t", emailFrom.strip())
    print("Destinatário:\t", deliveredTo.strip())
    print("Anexos:\t\t", arquivos if len(arquivos) > 0 else " Nenhum anexo !" )
    print("\n------------------------------\n")
    
    for i in arquivos:
        fileBase64_String = ""
        fileBase64 = open(i + "_base64_.txt", "r")
        
        for j in fileBase64:
            fileBase64_String += j.rstrip()
        
        with open(i, "wb") as fileAttachment:
            fileAttachment.write(base64.decodebytes(fileBase64_String.encode()))
