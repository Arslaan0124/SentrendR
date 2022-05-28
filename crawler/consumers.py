from cgitb import text
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print("USER",self.user.username)

        if self.user.is_authenticated:
            # accept connection if user is logged in
            await self.accept()

        else:
            # don't accept connection if user is not logged in 
            await self.close()

        self.room_name = self.user.username
        self.room_group_name = self.room_name
        print("room_name",self.room_name)
        print("room_group_name",self.room_group_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # await self.accept()
        self.connected = True

        await self.send(text_data=json.dumps({
            'type': 'websocket.accept',
            'message': str(self.user.username) + '. You are now connected'
        }))

        # while self.connected:
        #     await asyncio.sleep(2)
        #     await self.send(text_data=json.dumps({
        #     'type': 'websocket.accept',
        #     'message': 'You are now connected'
        # }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        # print("MESSAGE",text_data)
        # text_data_json = json.loads(text_data)
        message = text_data


        print("MESSAGE",message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))