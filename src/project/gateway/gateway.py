from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, StatusCode, Status, Logger
import socket
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
from RequisicaoRobo_pb2 import RequisicaoRobo
import random
from is_msgs.robot_pb2 import PathRequest
from is_msgs.robot_pb2 import RobotTaskRequest
from is_msgs.common_pb2 import Position
from google.protobuf.struct_pb2 import Struct
import json

log = Logger(name='Gateway')

def brokerAdd():
    config_paht = "config.json"
    fileAdr = open(config_paht, "r")
    brokerAdr = json.load(fileAdr)
    fileAdr.close()
    return brokerAdr["broker_uri"]

def controlRobo(requisicaoRobo, ctx):
    time.sleep(0.2)

    if requisicaoRobo.function == "Move":
        idPosition = RobotTaskRequest()
        idPosition.id = requisicaoRobo.id
        idPosition.basic_move_task.positions.extend([Position(
                                                x = requisicaoRobo.positions.x, 
                                                y = requisicaoRobo.positions.y, 
                                                z = requisicaoRobo.positions.z)])
        
        channel = Channel(brokerAdd())
        subscription = Subscription(channel)
        request = Message(content=idPosition, reply_to=subscription)
        channel.publish(request, topic="Controller.Set_position")
        
        try:
            reply = channel.consume(timeout=1.0)

        except socket.timeout:
            log.info('No reply :(')        # see this
    
        return Status(reply.status.code, why = reply.status.why)
      
    elif requisicaoRobo.function == "Get":

        struct = Struct()
        struct.fields["id"].number_value = requisicaoRobo.id

        channel = Channel(brokerAdd())
        subscription = Subscription(channel)
        request = Message(content=struct, reply_to=subscription)
        channel.publish(request, topic="Controller.Get_position")

        try:
            reply = channel.consume(timeout=1.0)
            position = reply.unpack(RobotTaskRequest)
            requisicaoRobo.positions.x = position.basic_move_task.positions[0].x
            requisicaoRobo.positions.y = position.basic_move_task.positions[0].y
            requisicaoRobo.positions.z = position.basic_move_task.positions[0].z
            return requisicaoRobo
      
        except socket.timeout:
            log.info('No reply :(')        # see this

while True:
    log.info("Inicializando")
    channel = Channel(brokerAdd())
    subscription = Subscription(channel)
    subscription.subscribe(topic="Controle.Console")
    log.info("Aguardando mensagens")

    message = channel.consume()

    messageString = message.body.decode('utf-8')
    time.sleep(1)

    log.info(messageString)
    randomNumber = random.randint(0, 2)
    if randomNumber == 1: #Sitema foi ligado
        messageOK = "Sistema ligado"
        log.info(messageOK)
        message = Message()
        message.body = messageOK.encode('utf-8')
        channel.publish(message, topic="Controle.Console")
        break
    
    else:
        messageLoss = "Tente novamente"
        log.info(messageLoss)
        message = Message()
        message.body = messageLoss.encode('utf-8')
        channel.publish(message, topic="Controle.Console")

channel = Channel(brokerAdd())
provider = ServiceProvider(channel)
logging = LogInterceptor()  # Log requests to console
provider.add_interceptor(logging)

provider.delegate(
    topic="Requisicao.Robo",
    function=controlRobo,
    request_type=RequisicaoRobo,
    reply_type=RequisicaoRobo)

provider.run()