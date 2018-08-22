# -*- coding: utf-8 -*-
# escrito para python 3
# cliente versão 16 - by alisson
# 05/05/2018 - 21:50


# importa bibliotecas de socket, sistema e hora
import socket
import sys
import time
import statistics
import os

import numpy as np
import scipy as sp
import scipy.stats

print('Socket TCP - Cliente \n')

# IP do servidor ao qual o cliente ira conectar
# host = input('Digite o IP para acesso ao servidor : ')
host = '192.168.15.140'

# porta tcp que o socket do lado cliente utilizara para realizar a comunicacao com o socket do  lado servidor
# port = int(input('Digite a porta tcp de acesso ao socket do servidor : '))
port = 5510

# variavel contendo tupla IP e porta do servidor
server_address = (host, port)

# Cria socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Estabelece a conexao do cliente com o servidor - utiliza o metodo connect
sock.connect(server_address)
print('\033[31mConectando no IP e porta do servidor : {}\033[m'.format(server_address))


#####################################################################################################################

# funcao para limpar outlier - metodo boxplot de john tukey - utiliza biblioteca numpy
def boxplot(data):
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    q1 = np.percentile(data, 25) - 1.5 * iqr
    q3 = np.percentile(data, 75) + 1.5 * iqr
    filtered = [n for n in data if (q1 < n < q3)]
    return filtered


# funcao para intervalo de confianca
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


# funcao para gerar cadeia de caracteres by alisson
def gerachar(size):
    chainchar = ''
    for x in range(0, size):
        chainchar = chainchar + 'a'
    return chainchar


# remove outliers
def reject_outliers(data):
    m = 2  # limite estipulado 2
    u = np.mean(data)  # retorna media dos elementos do array
    s = np.std(data)  # retorna desvio padrao dos elementos do array
    filtered = [e for e in data if (u - 2 * s < e < u + 2 * s)]
    return filtered



# define a quantidade amostras. Este numero sera utilizado para controlar o numero de repeticoes do "segundo laco"
qamostras = 2

# printa o tamanho do mss
# print(sock.getsockopt(socket.SOL_TCP, socket.TCP_MAXSEG))


# relacao de variaveis e listas globais
tempo = []
valores = []
valoresout = []
listamedia = []
listamediana = []
listadvp = []
totout = 0

try:

    # marca o inicio da coleta de amostras
    timeinicoleta = time.time()

    size = 0
    # primeiro laco
    # define volume de dados em byte que sera transmitido, potencia de 2 variando de : 1 ate 32768
    for j in range(0, 1):
        #size = 2 ** j
        size = 1024
        # print('potencia : {}'.format(size))

        message = gerachar(size)
        print('tamanho da messagem gerada pela funcao gerachar : {}\n'.format(len(message)))

        # zera valores de variaveis e listas
        tempo2 = []

        # segundo laco
        # controlado pelo numero de amostras definido na variavel "qamostras"
        for i in range(0, qamostras):
            # time.sleep(1)

            # regista o tempo do momento do envio
            timeSent = time.time()

            # envia os dados da variavel message pelo socket do cliente para conexao tcp
            sock.send(message.encode('ascii'))

            hourFrtSent = time.strftime("%H:%M:%S", time.localtime(time.time()))
            print('\033[32mEnviando {} as {} : {}\033[m'.format(i, hourFrtSent, str(len(message))))

            # time.sleep(3)

            contapkt = 0
            datarecv = ''
            while True:
                # aguarda envio de dados pelo servidor
                data = sock.recv(500000)
                # soma quantidade de bytes recebidos na mensagem enviada pelo servidor
                contapkt = len(data) + contapkt

                # concatena a mesagem fragmentada enviada pelo servidor
                datarecv = data.decode('ascii') + datarecv

                # registra o tempo no momento do recebimento
                timeReceived = time.time()
                hourFrtReceived = time.strftime("%H:%M:%S", time.localtime(time.time()))

                # converte o valor retornado pelo metodo ".time()" em segundos e milisegundos
                seg = (timeReceived - timeSent)
                ms = (timeReceived - timeSent) * 1000
                print(
                    '\033[34mRecebendo {} as {} : {}\033[m'.format(i, hourFrtReceived, str(len(data.decode('ascii')))))
                # print(sys.stderr, '\033[31mRTT :  milisegundos : {:0.3f} ms  segundos {:0.6f} s\033[m\n'.format(ms, seg))
                if contapkt == size:
                    break

            # print('tamanho da mensagem : {} conteudo {}'.format(str(len(data.decode('ascii'))), data.decode('ascii')))
            # print('tamanho da mensagem : {} conteudo {}'.format(str(len(datarecv)), datarecv))
            taxa = (size * 8) / seg
            print('\033[34mtamanho datarecv : {}\033[m'.format(len(datarecv)))
            print('\033[31mRTT :  milisegundos: {:0.3f}ms  segundos: {:0.6f}s  taxa: {:0.1f}bps\033[m\n'.format(ms, seg,
                                                                                                                taxa))

            # lista utilizada para salvar dados brutos - formato string : tamanho;tempo
            tempo.append(str(size) + ' ' + str(ms) + ' ' + str(taxa) + '\n')

            # lista utilizada para salvar somente os tempo de uma passada. A lista e zerada antes do inicio do laco
            tempo2.append(ms)

        # Retira outliers utiliza metodo boxplot
        # outliers=reject_outliers(tempo2)
        outliers = boxplot(tempo2)
        totout = len(outliers)

        ############  calculos solicitados no trabalho(media, mediana, DVP) ###################################
        media = statistics.mean(tempo2)
        mediaout = statistics.mean(outliers)
        # print('imprime media por statistic : {} \n'.format(media))

        mediana = statistics.median(tempo2)
        medianaout = statistics.median(outliers)
        # print('imprime mediana por statistic : {} \n'.format(mediana))

        dvp = statistics.pstdev(tempo2)
        dvpout = statistics.pstdev(outliers)
        # print('imprime dvp 2 por statistic : {} \n'.format(dvp))

        # funcao para medir intervalo de confianca, passa uma lista com os tempo, retorna media, valor minimo e maximo do intervalo
        a, b, c = mean_confidence_interval(tempo2)
        aout, bout, cout = mean_confidence_interval(outliers)
        # print('media: {} para baixo: {} para cima: {} \n' .format(a, b, c))

        # taxa de transferencia em bps - com e sem outliers
        taxamedia = (size * 8) / (media / 1000)
        taxamediaout = (size * 8) / (mediaout / 1000)

        ##### salva as passagens de 1 ate 32768, valores em arquivo :  tamanho, media, media, DVP, intervalo de conficanca, taxa de transferencia
        valores.append(
            str(j) + ' ' + str(media) + ' ' + str(mediana) + ' ' + str(dvp) + ' ' + str(a) + ' ' + str(b) + ' ' + str(
                c) + ' ' + str(round(taxamedia)) + '\n')
        valoresout.append(
            str(j) + ' ' + str(mediaout) + ' ' + str(medianaout) + ' ' + str(dvpout) + ' ' + str(aout) + ' ' + str(
                bout) + ' ' + str(cout) + ' ' + str(round(taxamediaout)) + ' ' + str(totout) + '\n')

        # variancialista.append(str(variancia)+'\n')
        # print('tamanho, media , mediana e dvp : {} ; {} ; {} ; {} ' . format(str(size), str(media), str(mediana), str(dvp)))

        listamedia.append(str(j) + ' ' + str(media) + ' ' + str(dvp) + '\n')
        listamediana.append(str(j) + ' ' + str(mediana) + '\n')
        listadvp.append(str(j) + ' ' + str(dvp) + '\n')


finally:
    # marca o fim da coleta
    timefimcoleta = time.time()
    print('Tempo total de coleta: {}'.format(timefimcoleta - timeinicoleta))

    # encerra o socket de conexão
    pid = os.getpid()
    sock.close()


    print('Terminando socket\n')


    # Abre o arquivo bruto-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/bruto-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d", time.localtime(
        time.time())) + '-' + str(time.time()) + '.txt', 'a')
    # grava os valores brutos : size, tempo em milisegundo
    arq.writelines(tempo)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

    # Abre o arquivo valores-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/valores-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d",
                                                                                               time.localtime(
                                                                                                   time.time())) + '-' + str(
        time.time()) + '.txt', 'a')
    # grava os valores : size, media, media, dvp
    arq.writelines(valores)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

    # Abre o arquivo valores sem outliers-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/valoresout-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d",
                                                                                                  time.localtime(
                                                                                                      time.time())) + '-' + str(
        time.time()) + '.txt', 'a')
    # grava os valores : size, media, media, dvp
    arq.writelines(valoresout)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

    # Abre o arquivo media-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/media-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d", time.localtime(
        time.time())) + '-' + str(time.time()) + '.txt', 'a')
    # grava os valores : size, media
    arq.writelines(listamedia)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

    # Abre o arquivo mediana-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/mediana-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d",
                                                                                               time.localtime(
                                                                                                   time.time())) + '-' + str(
        time.time()) + '.txt', 'a')
    # grava os valores : size, mediana
    arq.writelines(listamediana)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

    # Abre o arquivo dvp-DATA DO DIA.txt e grava os RTT registrados
    arq = open('./resultados/dvp-' + str(pid) + '-' + str(qamostras) + '-' + time.strftime("%Y-%m-%d", time.localtime(
        time.time())) + '-' + str(time.time()) + '.txt', 'a')
    # grava os valores : size, dvp
    arq.writelines(listadvp)
    # fecha o arquivo tempo-DATA DO DIA.txt
    arq.close()

