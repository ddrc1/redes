import socket, pickle, time


server_port = 22000
server_buffer = 1024
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((socket.gethostname(), server_port))

while True:
    packet, client_ip = server_socket.recvfrom(server_buffer)
    recv_packet = pickle.loads(packet)
    print("Pacote recebido:", recv_packet)

    index_recv = recv_packet['index']
    time_str = str(time.time())
    time_bytes = time_str.encode("UTF-8")

    send_packet = {'index_recv': index_recv,
                   'time': time_bytes}
    print("ACEITO")
    server_socket.sendto(pickle.dumps(send_packet), (client_ip[0], client_ip[1]))


