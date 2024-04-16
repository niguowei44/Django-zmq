from django.urls import re_path
from app01 import consumers

websocket_urlpatterns = [
    #re_path(r'room/(?P<group>\w+)/$', consumers.ChatConsumer.as_asgi()),  # 路由匹配 组名为group (?P<group>)/$固定写法 \w+匹配任意字母数字下划线
    re_path(r'zmq/(?P<group>\w+)/$', consumers.ZeroMQConsumer.as_asgi()),  # 路由匹配

]
