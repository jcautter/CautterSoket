import socket
from typing import NewType

ConnType = NewType('Connection Type', str)
MSGConn = NewType('MSG CONN', bytes)

class CautterSoket:
    Sender = ConnType('Sender')
    Receiver = ConnType('Receiver')
    
    MSG_HLLO = MSGConn(b'MSG_HLLO')
    MSG_OK = MSGConn(b'MSG_OK')
    MSG_SEND_FILE = MSGConn(b'MSG_SEND_FILE')
    MSG_SEND_FILE_VALID = MSGConn(b'MSG_SEND_FILE_VALID')
    MSG_RECEIVE_FILE = MSGConn(b'MSG_RECEIVE_FILE')
    MSG_RECEIVE_FILE_VALID = MSGConn(b'MSG_RECEIVE_FILE_VALID')
    MSG_SEND_FILE_FINISHED = MSGConn(b'MSG_SEND_FILE_FINISHED')
    MSG_SEND_FILE_FINISHED_VALID = MSGConn(b'MSG_SEND_FILE_FINISHED_VALID')


    def __init__(self, host, port, buffer_size=1024, www=False):
        self.buffer_size = buffer_size
        self.__get_host()
        self.__create_soket()
        self.__conn_host_ip = host
        if www:
            self.__conn_host_ip = self.__local_host_ip
        self.__conn_port = port
        self.__remote_host_ip = None
        self.__conn = None
    @property
    def buffer_size(self):
        return self.__buffer_size
    @buffer_size.setter
    def buffer_size(self, val:int):
        self.__buffer_size = val
    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self, val:bytes):
        self.__data = val
    @property
    def remote_host_ip(self):
        return self.__remote_host_ip
    def __get_host(self):
        self.__local_host_name = socket.gethostname()
        self.__local_host_ip = socket.gethostbyname(self.__local_host_name)
    def __create_soket(self):
        self.__soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def show_host(self):
        print('host name', self.__local_host_name)
        print('host ip', self.__local_host_ip)
        if self.__remote_host_ip is not None:
            print('remote host:', self.__remote_host_ip)
    def connect(self, host=None, port=None):
        if host is None:
            host = self.__conn_host_ip
        if port is None:
            port = self.__conn_port
        self.__soket.connect((host, port))
        self.__conn = self.__soket
    def receiver(self, host=None, port=None, buffer_size:int=None, www=False):
        if host is None:
            host = self.__conn_host_ip
        if port is None:
            port = self.__conn_port
        if buffer_size is not None:
            buffer_size = self.buffer_size
        if www:
            host = self.__local_host_ip
        self.__soket.bind((host, port))
        self.__soket.listen()
        self.__conn, self.__remote_host_ip = self.__soket.accept()
    def sendall(self, val:bytes, log=False):
        if self.__conn is not None:
            self.__conn.sendall(val)
            if log:
                print('Msg Sent:', val)
        else:
            print('Information:', 'No connection to send data')
    def __sendall_valid(self, val:bytes, log=False):
        if self.__conn is not None:
            while True:
                self.sendall(val, log=log)
                data = self.receive(log=log)
                if data == self.MSG_OK:
                    break
                else:
                    self.sendall(val, log=log)
        else:
            print('Information:', 'No connection to send data')
    def sendall_valid(self, msg:bytes, val:bytes, log=False):
        if self.__conn is not None:
            if msg[-6:] == b'_VALID':
                self.__sendall_valid(msg, log=log)
                self.__sendall_valid(val)
            else:
                print('Information:', 'MSG is not VALID kind', msg)    
        else:
            print('Information:', 'No connection to send data')
    def receive(self, buffer_size:int=None, log=False):
        if self.__conn is not None:
            if buffer_size is None:
                buffer_size = self.buffer_size
            self.data = self.__conn.recv(buffer_size)
            if log:
                print('Msg Received:', self.data)
            return self.data
        else:
            print('Information:', 'No connection to receive data')
    def close(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None
    def send_file(self, path, buffer_size=None, log=False, validation=False):
        if self.__conn is not None:
            if buffer_size is None:
                buffer_size = self.buffer_size
            #msg = b'Vou mandar o arquivo!'
            self.sendall(self.MSG_SEND_FILE, log=log)

            data = self.receive(log=log)
            if data == self.MSG_OK:
                with open(path, 'rb') as f:
                    l = f.read(buffer_size)
                    while True:
                        if not l:
                            f.close()
                            break
                        self.sendall(l)
                        l = f.read(buffer_size)
                #msg = b'Acabou, enviei tudo!'
                self.sendall(self.MSG_SEND_FILE_FINISHED, log=log)
            self.close()
            print('Information:','connection closed')
        else:
            print('Information:', 'No connection to send file')
    def receive_file(self, path, buffer_size=None, log=False, validation=False):
        if self.__conn is not None:
            if buffer_size is None:
                buffer_size = self.buffer_size
            print('Information:', 'Connected by', self.remote_host_ip)
            data = self.receive(log=log)
            if data == self.MSG_SEND_FILE:
                #msg = b'Ta beleza, pode mandar'
                self.sendall(self.MSG_OK, log=log)
                with open(path, 'wb') as f:
                    while True:
                        data = self.receive(buffer_size)
                        if data==self.MSG_SEND_FILE_FINISHED:
                            print('mensagem recebida:', repr(data))
                            break
                        f.write(data)
                    f.close()
                    print('Information:','Successfully get the file')
                        
                self.close()
                print('Information:','connection closed')
        else:
            print('Information:', 'No connection to receive file')
