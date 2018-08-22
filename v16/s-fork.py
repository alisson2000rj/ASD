# -*- coding: utf-8 -*-
# escrito para python 3
#cliente versão 16 - by alisson
# 05/05/2018 - 21:50


#importa bibliotecas de socket, sistema e hora
import os
import socket
import sys
import time



print('Socket TCP - Servidor \n')
# IP que o servidor utilizarÃ¡ para receber a comunicacao do clientes
#host = input('Digite o IP que o socket utilizarÃ¡ : ')
host="192.168.15.140"

# porta que o socket do servidor utilizara para receber comuicacao enviada pela camada de transporte
#port = int(input('Digite a porta tcp para comunicaÃ§Ã£o do socket com a conexÃ£o TCP : '))
port=5510
server_address = (host, port)

# Cria um socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print ('\033[31mIniciando servico de socket -> {}\033[m'.format(server_address))

# Estabalece o IP e a porta de entrada
sock.bind((server_address))

# Faz com que o servidor escute na porta designada, especifica um numero para fila de processos
sock.listen(4)

# variavel contadora que estipula numero de conexoes concorrentes
i=1

#limita o numero de conexoes concorrentes ate 4
while i<=4:

    # Cria um novo socket no servidor chamado server dedicado a este cliente especifico
    server, client_address = sock.accept()
    print('\033[31mEspererando por conexÃ£o !\033[m')

    # Inicia um processo filho, que permitira a utilizacao de conexoes concorrentes
    #child_pid=os.fork()
    child = os.fork()
    child_pid = os.getpid()
    print('pid do child : {} \n' .format(child))


    print('valor de child pid {}'.format(child_pid))

    if child:
        print('\n\n \033[31mConexÃ£o estabelecida por cliente {} : {}\033[m'.format(str(i), client_address))
        #print('valor de child pid {}'.format(child_pid))
        while True:

            # aguarda envio de dados pelo cliente
            #print('Aguardando dados!\n')
            data = server.recv(1024)
            #data = server.recv(32768)
            #print('data : {}'.format(data))
            #print('data decode : {}'.format(data.decode()))

            #print('Dados recebido!\n')
            #data = server.recv(128)
            #print(data.decode())
            # registra o tempo no momento do recebimento
            timeReceived = time.time()
            hourFrtReceived = time.strftime("%H:%M:%S", time.localtime(time.time()))

            #decoded_data = data.decode()

            if not (data.decode('ascii')):
                # encerra a conexao caso o cliente pare de enviar dados
                server.close()
                print('\nConexao com o Cliente {} Finalizada'.format(str(i)))
                break

            else:
                # imprime messagem enviada pelo cliente e mostra qual o seu tamanho
                print('\033[34mRecebendo as {} do CLIENTE {} : {} \033[m'.format(hourFrtReceived, str(i), str(len(data))))

                # envia uma mensagem para o cliente
                #Utilizado para reduzir string- teste
                #message = data.decode()[0:10]
                message = data.decode('ascii')
                server.send(message.encode('ascii'))
                timeSent = time.time()
                hourFrtSent = time.strftime("%H:%M:%S", time.localtime(time.time()))
                #seg = (timeSent - timeReceived)
                #ms = (timeSent - timeReceived) * 1000
                print('\033[32mEnviando as {} para o CLIENTE {} : {} \033[m\n'.format(hourFrtSent, str(i), str(len(message))))
                #print(sys.stderr, '\033[31mRTT :  milisegundos : {:0.3f} ms  segundos {:0.6f} s\033[m\n'.format(ms, seg))

    else:
        #incrementa mais uma conexao ao controle
        i+=1

