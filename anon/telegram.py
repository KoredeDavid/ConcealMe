import json
import os
import requests
import time
from .models import Telegram


TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    try:
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content
    except:
        pass


def get_json_from_url(url):
    try:
        content = get_url(url)
        js = json.loads(content)
        return js
    except:
        pass


def get_updates():
    try:
        url = URL + "getUpdates"
        js = get_json_from_url(url)
        return js
    except:
        pass


'''
if offset:
url += "?offset={}".format(offset)
'''


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


dic = {"ok": True, "result": [{"update_id": 119993455,
                               "message": {"message_id": 73,
                                           "from": {"id": 709170277, "is_bot": False, "first_name": "David",
                                                    "username": "KoredeDavid", "language_code": "en"},
                                           "chat": {"id": 709170277, "first_name": "David", "username": "KoredeDavid",
                                                    "type": "private"}, "date": 1592755102, "text": "Anon-David-1"}},
                              {"update_id": 119993456,
                               "message": {"message_id": 208,
                                           "from": {"id": 709170277, "is_bot": False, "first_name": "David",
                                                    "username": "KoredeDavid", "language_code": "en"},
                                           "chat": {"id": 709170277, "first_name": "David", "username": "KoredeDavid",
                                                    "type": "private"}, "date": 1592776298, "text": "HI LOVE"}},
                              {"update_id": 119993457,
                               "message": {"message_id": 208,
                                           "from": {"id": 709170277, "is_bot": False, "first_name": "David",
                                                    "username": "KoredeDavid", "language_code": "en"},
                                           "chat": {"id": 709170277, "first_name": "David", "username": "KoredeDavid",
                                                    "type": "private"}, "date": 1592776298, "text": "Anon-wisdom-43"}}]}


def get_last_chat_id_and_text(updates=get_updates()):
    try:
        if len(updates["result"]) > 0:
            num_updates = len(updates["result"])
            last_update = num_updates - 1
            text = updates["result"][last_update]["message"]["text"]
            chat_id = updates["result"][last_update]["message"]["chat"]["id"]
            if text in Telegram.objects.all().values_list('anon_user_id', flat=True):
                Anon, my_username, pk = text.split('-')
                if Telegram.objects.get(user__username__iexact=my_username).anon_user_id == text:
                    update = Telegram.objects.get(user__username__iexact=my_username)
                    update.telegram_id = chat_id
                    update.telegram_switch = True
                    update.save()
                    print(text, chat_id)
    except:
        pass


"""Telegram.objects.filter(user__username__iexact=my_username).delete() Telegram.objects.create(
user=CustomUser.objects.get(username__iexact=my_username), telegram_id=chat_id, anon_user_id=text, 
telegram_switch=True) """


def tel(message):
    return '\n\n'.join(map(str, message))


def send_telegram_message(text, chat_id):
    try:
        url = URL + "sendMessage?text={}&chat_id={}".format(tel(text), chat_id)
        get_url(url)
    except:
        pass


def send_telegram_message2(text, chat_id):
    try:
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        get_url(url)
    except:
        pass


def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_telegram_message(text, chat)
        except Exception as e:
            print(e)


# text, chat = get_last_chat_id_and_text(get_updates())
# send_message(text, chat)


def main():
    last_update_id = None
    while True:
        updates = get_updates()
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
