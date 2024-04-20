# zeromq_publisher.py
import zmq
import time
import random

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")  # 绑定到所有接口的5556端口

while True:

    data = f"Hello from ZeroMQ - {random.randint(1, 100)}"
    socket.send_string(data)
    print(f'Sent: {data}')
    time.sleep(1)  # 每秒发送一条消息

