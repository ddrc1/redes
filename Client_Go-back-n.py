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

    # Envio de pacotes
    # O resto do algoritmo não pode ter visão do que ocorre aqui
    print("\n- - - - - - - Tentativa de enviar pacotes - - - - - -")
    for packet in window:
        time.sleep(1)
        # Simular chance de não enviar para o servidor
        if random.randint(0, 9) > 2:
            print("Enviou pacote", packet)
            client_socket.sendto(pickle.dumps(packet), (socket.gethostname(), server_port))
        else:
            print("Pacote perdido", packet)

    # Receber confirmação do servidor
    print("\n- - - - - - - Recebimento de ACK - - - - - -")
    len_window = len(window)
    for i in range(len_window):
        try:
            packet, server_ip = client_socket.recvfrom(cliente_buffer)
            recv_packet = pickle.loads(packet)

            # Verifica se o tempo do ultimo envio equivale ao tempo vindo no pacote, se não for, significa que o pacote
            # recebido é de uma requisição falhada anteriormente
            time.sleep(1)
            print("ACK recebido:", recv_packet)

            # Validação e deslize de janela
            if recv_packet['expected_index'] == window[0]['index']:
                print("VALIDADO")
                start += 1
                if start == len(vector_packets) and window[0]['end'] == '0'.encode("UTF-8"):
                    nextPos = start
                    done = False
                if window[0]['end'] == '1'.encode("UTF-8"):
                    done = True
                del window[0]
            else:
                print("ERRO!")
                nextPos = start
                window = []
                done = False

        # Timeout
        except:
            nextPos = start
            done = False
            window = []
            break
    if len(window) == len_window and done:
        nextPos = start
        window = []
        done = False

    print("\n- - - - - - - - - - - - - - - -\n")


