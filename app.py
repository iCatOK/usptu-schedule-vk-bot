# app.py
from flask import Flask, request, jsonify
from worker import login, paralel_time_check_update
import vk_api_sender
import os
import vk
import json
import random

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
confirmation_token = os.environ.get("CONFIRMATION_TOKEN")

@app.route('/')
def hello_world():
    return 'Hello from BPO-18-01 BOT!'


# A welcome message to test our server
@app.route('/api/', methods=['POST'])
def processing():
    #Распаковываем json из пришедшего POST-запроса
    data = json.loads(request.data)
    print(data)
    #Вконтакте в своих запросах всегда отправляет поле типа
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation':
        return confirmation_token
    elif data['type'] == 'message_new':
        vk_api_sender.create_answer(data['object'])
        print('return OK to VK - message new')
        return 'ok'
    elif data['type'] == 'update_schedule':
        paralel_time_check_update()
        return 'pending, cool'
    print('return OK to VK - other')
    return 'ok'



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
