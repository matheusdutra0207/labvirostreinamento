from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, Logger, StatusCode
import socket
from RequisicaoRobo_pb2 import RequisicaoRobo
from is_msgs.common_pb2 import Position
import time
import json
import random

log = Logger(name='Interface')

def brokerAdd():
    config_paht = "config.json"
    fileAdr = open(config_paht, "r")
    brokerAdr = json.load(fileAdr)
    fileAdr.close()
    return brokerAdr["broker_uri"]

while True:
    #send mensage to system 
    log.info("Inicializando")
    messageOn = "Ligar sistema"
    channel = Channel(brokerAdd())
    message = Message()
    message.body = messageOn.encode('utf-8')
    channel.publish(message, topic="Controle.Console")

    #waiting for answer
    subscription = Subscription(channel)
    subscription.subscribe(topic="Controle.Console")
    log.info("Aguardando mensagens")
    message = channel.consume()
    message.body.decode('utf-8')

    if message.body.decode('utf-8') == "Sistema ligado":
        log.info(message.body.decode('utf-8'))
        break

    log.info(message.body.decode('utf-8'))
    time.sleep(1)

while True:
    time.sleep(1)
    requestRobo = RequisicaoRobo()
    requestRobo.id = random.randint(1, 3)
    requestRobo.function = "Get" if random.randint(1, 2) == 1 else "Move"
    if requestRobo.function == "Move":          
        requestRobo.positions.x = random.randint(1, 5)
        requestRobo.positions.y = random.randint(1, 5)
        requestRobo.positions.z = random.randint(-2, 6)


    channel = Channel(brokerAdd())
    subscription = Subscription(channel)
    request = Message(content=requestRobo, reply_to=subscription)
    channel.publish(request, topic="Requisicao.Robo")

    try:
        reply = channel.consume(timeout=2.0)

    except socket.timeout:
        log.info('No reply :(')


    if reply.unpack(RequisicaoRobo).function == "Get":
        position = reply.unpack(RequisicaoRobo)
        log.info(f'Robot {position.id} position: {(position.positions.x, position.positions.y, position.positions.z)}')

    
        
