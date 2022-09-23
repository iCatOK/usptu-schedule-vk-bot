import vk
import random
import os
from threading import Thread
from worker import make_csv, check_update, debug_delete_last
from emoji import emojize


session = vk.Session()
api = vk.API(session, v='5.110')
token = os.environ.get("ACCESS_TOKEN")


def send_message_user(user_id, message):
    api.messages.send(
        access_token=token, 
        user_id=user_id, message=message, 
        random_id=random.getrandbits(64)
    )


def send_message_chat(peer_id, message):
    api.messages.send(
        access_token=token, 
        peer_id=peer_id, message=message, 
        random_id=random.getrandbits(64)
    )

def parralel_make_csv(msg_kwargs):
    print('работа в потоке начата')
    last_link = make_csv()
    print('Создана таблца из makecsv')
    message = emojize(':closed_book: Следующая пара: {}\nСсылка: {}'.format(last_link[0], last_link[1]))
    msg_kwargs['message'] = message
    method = msg_kwargs.pop('method')
    sending[method](**msg_kwargs)
    print('работа в потоке завершена')

def parralel_check_update(msg_kwargs):
    print('работа в потоке начата')
    last_link = check_update()
    print('Обновлена таблица data csv')
    message = emojize(':closed_book: Следующая пара: {}\nСсылка: {}'.format(last_link[0], last_link[1]))
    msg_kwargs['message'] = message
    method = msg_kwargs.pop('method')
    sending[method](**msg_kwargs)
    print('работа в потоке завершена')

def get_document_url(msg_kwargs):
    url = msg_kwargs.pop('attachment')
    method = msg_kwargs.pop('method')
    msg_kwargs['message'] = url
    sending[method](**msg_kwargs)

def parralel_debug_delete_last(msg_kwargs):
    print('работа в потоке начата')
    debug_delete_last()
    msg='Удалена последняя запись data csv'
    print(msg)
    msg_kwargs['message'] = msg
    method = msg_kwargs.pop('method')
    sending[method](**msg_kwargs)
    print('работа в потоке завершена')


commands = {
    'ДО собери расписание': parralel_make_csv,
    'ДО какая пара': parralel_check_update,
    'ДО дебаг удали последний': parralel_debug_delete_last,
    
}

file_commands = {
    'ДО загрузи документ': get_document_url,
}

sending = {
    'chat': send_message_chat,
    'user': send_message_user
}

def command_handler(msg_kwargs):
    proccessing_kwargs = msg_kwargs.copy()
    if msg_kwargs['message'] in commands.keys():
        t = Thread(
            target=commands[msg_kwargs['message']], 
            args=[proccessing_kwargs]
        )
    elif msg_kwargs['message'] in file_commands.keys():
        t = Thread(
            target=file_commands[msg_kwargs['message']], 
            args=[proccessing_kwargs]
        )
        msg_kwargs.pop('attachment')
    else:
        return
    t.start()
    method = msg_kwargs.pop('method')
    msg_kwargs['message'] = 'Обработка'
    sending[method](**msg_kwargs)
     
        


def create_answer(object):
    msg_kwargs = {}
    
    if 'user_id' in object.keys():
        user_id = object['user_id']
        message = object['body']
        msg_kwargs = {
            'user_id': user_id,
            'message': message,
            'method': 'user'
        }
        # Сообщение о том, что обработка прошла успешно
    elif 'message' in object.keys():
        if len(object['message']['attachments']) > 0:
            attachment = object['message']['attachments'][0]
            if attachment['type'] == 'doc':
                url_doc = attachment['doc']['url']
                msg_kwargs['attachment'] = url_doc
        msg_kwargs['peer_id'] = object['message']['peer_id']
        msg_kwargs['message'] = object['message']['text']
        msg_kwargs['method'] = 'chat'
    command_handler(msg_kwargs)