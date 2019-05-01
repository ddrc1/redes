import socket,pickle, time


server_port = 22000
server_buffer = 1024
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((socket.gethostname(), server_port))

expected_index = 0

while True:
    packet, client_ip = server_socket.recvfrom(server_buffer)
    recv_packet = pickle.loads(packet)
    print("Pacote recebido:", recv_packet)

    expected_index = str(expected_index)
    expected_index_bytes = expected_index.encode("UTF-8")
    time_str = str(time.time())
    time_bytes = time_str.encode("UTF-8")

    # Verificar se os valores recebidos não estão corrompidos
    if recv_packet['index'] == expected_index_bytes:
        send_packet = {'expected_index': expected_index_bytes,
                       'time': time_bytes}
        print("ACEITO")
        expected_index = int(expected_index) + 1
        server_socket.sendto(pickle.dumps(send_packet), (client_ip[0], client_ip[1]))
        if recv_packet['end'] == '1'.encode("UTF-8"):
            expected_index = 0
            print("- - - - - - - - - Nova Requisição - - - - - - - - -")
    else:
        print("REJEITADO")
        send_packet = {'expected_index': recv_packet['index'],
                       'time': time_bytes}
        server_socket.sendto(pickle.dumps(send_packet), (client_ip[0], client_ip[1]))


