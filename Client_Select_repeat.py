import socket, pickle, random, time, math


def text_vecPackets(client_msg_bytes, packet_bytes):
    vector_packets = []
    index = 0
    count_aux = 0
    for i, byte in enumerate(client_msg_bytes):
        data = client_msg_bytes[count_aux : i]
        index = str(index)
        index_bytes = index.encode("UTF-8")

        # Verifica se é o final da mensagem
        if i != len(client_msg_bytes) - 1:
            end = "0".encode('UTF-8')
        else:
            end = "1".encode('UTF-8')

        # Verifica se o somatorio das informações corresponde ao tamanho do pacote
        if len(data) + len(index_bytes) + len(end) == packet_bytes:
            packet = {'index': index_bytes,
                      'end': end,
                      'data': data}
            vector_packets.append(packet)
            index = int(index_bytes.decode("UTF-8")) + 1
            count_aux = i
        elif i == len(client_msg_bytes) - 1:
            packet = {'index': index_bytes,
                      'end': end,
                      'data': data}
            vector_packets.append(packet)
    return vector_packets


def send_packets(window):
    # Envio de pacotes
    print("\n- - - - - - - Tentativa de enviar pacotes - - - - - -")
    for packet in window:
        time.sleep(1)
        # Simular chance de não enviar para o servidor
        if random.randint(0, 9) > 2:
            print("Pacote enviado", packet)
            client_socket.sendto(pickle.dumps(packet), (socket.gethostname(), server_port))
        else:
            print("Pacote perdido", packet)


def receive_ack(window, vector_packets):
    # Receber confirmação do servidor
    print("\n- - - - - - - Recebimento de ACK - - - - - -")
    window_sent = []
    window_len = len(window)
    for i in range(window_len):
        try:
            packet, server_ip = client_socket.recvfrom(cliente_buffer)
            recv_packet = pickle.loads(packet)
            time.sleep(1)
            print("ACK recebido:", recv_packet)
            index_recv = int(recv_packet['index_recv'].decode("UTF-8"))
            window_sent.append(vector_packets[index_recv])
        except :
            pass

    # Verificação de ACKs não recebidos
    window_aux = []
    while window:
        if window[0] not in window_sent:
            send_packets([window[0]])
            window_aux.append(window[0])
        del window[0]

    # Reenvio de pacotes
    if window_aux != []:
        receive_ack(window_aux, vector_packets)


# Dados do cliente
server_port = 22000
cliente_buffer = 1024
client_msg = "teste 1, teste 2, teste 3, teste 4, teste 5, teste 6, teste 7, teste 8, teste 9, teste 10" + "."
client_msg_bytes = client_msg.encode("UTF-8")

# criação do socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(3)

# Criação da janela
start = 1
nextPos = 1
window_size = 3                 #Alteravel
send_time_s = 12                #Alteravel
window = []

# Divisão da string em pacotes
packet_qnt = 10                   #Alteravel
packet_bytes = len(client_msg_bytes) / packet_qnt  #Min (data + header)
vector_packets = text_vecPackets(client_msg_bytes, math.ceil(packet_bytes))
print(vector_packets)
done = False

while not done:

    # Verificar se a janela está cheia
    while nextPos < start + window_size and not done:
        window.append(vector_packets[nextPos - 1])
        nextPos += 1
        print("Janela:", window)
        if len(vector_packets) == nextPos - 1:
            done = True

    # Registra o tempo antes de enviar os pacores
    send_time = time.time()

    send_packets(window)

    receive_ack(window, vector_packets)

    start = nextPos
    print("\n- - - - - - - - - - - - - - - -\n")
