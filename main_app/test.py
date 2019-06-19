import IBM_STT

import socket
import json
import time
import subprocess


class MessageSender:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect((self.host, self.port))

    def send(self, message):
        self.client.send(message.encode('utf-8'))
        # response = self.client.recv(4096)  # レシーブは適当な2の累乗にします（大きすぎるとダメ）
        # print(response)

    def disconnect(self):
        self.client.close()


def send_message(message):
    message_sender.send(message)


def callback_fn(texts):
    print('--- START SEND ---')
    for text in texts:
        data = {
            "meta": {
                "type": "speechText"
            },
            "data": {
                "text": text,
                "isInterrupt": False
            }
        }
        body = json.dumps(data, ensure_ascii=False)
        print(text)
        send_message(body)
        time.sleep(1)
    message_sender.disconnect()
    print('--- END SEND ---')


def init():
    message_sender.connect()
    ibm_stt = IBM_STT.IBM_STT('sound_data/sample_08.mp3', callback_fn)
    ibm_stt.stt()


if __name__ == '__main__':
    message_sender = MessageSender('127.0.0.1', 3939)
    init()
