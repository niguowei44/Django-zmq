import asyncio
import json
import zmq
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from zmq.asyncio import Context


# 类似于服务端
class ChatConsumer(WebsocketConsumer):
    """
    至少三个方法：websocket_connect, websocket_receive, websocket_disconnect
    握手成功后，WebSocket连接就建立了，此时可以开始发送和接收消息。
    """
    def websocket_connect(self, message):
        """
        当WebSocket连接建立时调用
        """
        print("WebSocket握手成功，连接建立")
        self.accept()  # 接受连接
        # self.send("收到消息")  # 服务器主动发送消息到客户端
        group = self.scope["url_route"]["kwargs"].get("group")  # 获取routing.py中websocket创建的路由中的group参数
        async_to_sync(self.channel_layer.group_add)(group, self.channel_name)  # 加入num组 异步  --> 需要转化成同步

    def websocket_receive(self, message):
        """
        当服务端接收到消息时调用
        message 消息格式：{'type': 'websocket.receive', 'text': '收到的消息'}
        """
        group = self.scope["url_route"]["kwargs"].get("group")
        async_to_sync(self.channel_layer.group_send)(group, {"type": "receive.message", "message": message})  # 向前端所有在num组发送消息 使用receive.message方法 异步  --> 需要转化成同步

    def receive_message(self, event):  # 前端发送的消息转到后端 接收到消息时调用
        text = event['message']['text']  # 获取消息内容
        if text == "close":  # 如果接收到关闭消息，服务器关闭连接与客户端的连接 执行html内的onclose事件
            self.close()
            raise StopConsumer()  # 服务器主动断开连接 不会执行websocket_disconnect方法 不加词函数，客户端处也会断开连接执行websocket_disconnect方法
        else:
            self.send(text)  # 发送消息到客户端 (HTML页面)

    def websocket_disconnect(self, message):  # 连接断开时调用
        group = self.scope["url_route"]["kwargs"].get("group")
        async_to_sync(self.channel_layer.group_discard)(group, self.channel_name)
        print("有客户端主动断开连接")  # 客户端(HTML页面)断开连接时 打印断开连接信息 包括关闭浏览器
        raise StopConsumer()  # 服务器主动断开连接


class ZeroMQConsumer(AsyncWebsocketConsumer):
    """
    zeromq 异步收发消息
    订阅-发布模式
    """
    async def connect(self):
        """
        WebSocket连接建立时调用
        """
        await self.accept()

        # 设置ZeroMQ订阅者
        self.context = Context()  # 使用zmq的异步模式创建上下文 否则会阻塞
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5556")  # 连接到ZeroMQ发布者
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")  # 订阅所有消息
        # 开始从ZeroMQ接收消息并转发给WebSocket
        await self.forward_zeromq_messages()

    async def forward_zeromq_messages(self):
        while True:
            try:
                message = await self.socket.recv_string()

                await self.send(text_data=json.dumps({'message1': message}))
                print(json.dumps({'message1': message}))  # {"message1": "具体消息"}
            except zmq.error.ZMQError:
                # 如果ZMQ连接中断，重新连接
                self.socket = self.context.socket(zmq.SUB)
                self.socket.connect("tcp://localhost:5556")
                self.socket.setsockopt_string(zmq.SUBSCRIBE, "")  # 订阅所有消息

    async def disconnect(self, close_code):
        # 断开连接时关闭ZeroMQ订阅者
        self.socket.close()
        self.context.term()
        print("断开连接")
        await super().disconnect(close_code)
