import json
import time

import requests
import random
import copy

# from .telegram import get_last_chat_id_and_text
# a = requests.get('https://api.telegram.org/bot1201362749:AAGnJUeZYc97DQG-HuonZq31MbmOlPXehi4/sendMessage?chat_id=709170277&text=You are a fine boy \n realirrrwrt')
updates = {
    "ok": True, "result": {"message_id": 20, "from": {"id": 1201362749, "is_bot": True,
                                                      "first_name": "KoredeDavid", "username": "KoredeDavidBot"},
                           "chat": {"id": 709170277, "first_name": "David", "username": "KoredeDavid",
                                    "type": "private"},
                           "date": 1592135722, "text": "You are a fine boy \n realirrrwrt",
                           'user_id': random.randint(a=1, b=2)}
}

a = ['love', 'like', 'care', 'disgust', 'fight']
(a.remove(a[1]))
print(a)
pot = ['hate']
print(pot)
reset = list(set(a) ^ set(pot))
# uncommon = list(reset)
common = (list(set(a) & set(pot)))
print(reset)
print(common)

user_id = {'user_id': 1}

# merge = {**dic, **user_id}
# print(merge)


'''
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
                                                    "type": "private"}, "date": 1592776298, "text": "Anon-Deji-"}}]}

print(len(dic["result"]))


# print(dic)
# userid = {'user_id': 1}
#
# merge = {**dic, **user_id}
# print(merge)

items = ['like', 'love', 'hate']


TOKEN = "1201362749:AAGnJUeZYc97DQG-HuonZq31MbmOlPXehi4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js


'''

# !/bin/python3

import math
import os
import random
import re
import sys


# Complete the rotLeft function below.
def rotLeft(an=None, d=13):
    # a = [33, 47, 70, 37, 8, 53, 13, 93, 71, 72, 51, 100, 60, 87, 97]
    if an is None:
        an = [33, 47, 70, 37, 8, 53, 13, 93, 71, 72, 51, 100, 60, 87, 97]

    print(an[d:])
    print(an[:d])


rotLeft()
kiki = 'love'
bibi = 'hate'
love = list('love')
bro = list('br')
summer = bro + love
vote = list(set(love) & set(bro))
print(vote)

home = [1, 2, 3, 4, 5]


# print(map(list(home), home))


def isReachable(sx, sy, dx, dy):
    # base case
    if (sx > dx or sy > dy):
        return False

    # current point is equal to destination
    if (sx == dx and sy == dy):
        return True

    # check for other 2 possibilities
    return (isReachable(sx + sy, sy, dx, dy) or
            isReachable(sx, sy + sx, dx, dy))


source_x, source_y = 2, 10
dest_x, dest_y = 26, 12
if (isReachable(source_x, source_y, dest_x, dest_y)):
    print("True")
else:
    print("False")
# Driver code


text = 'customer_id	first_name	last_name	gender	past_3_years_bike_related_purchases	DOB	job_title	job_industry_category	wealth_segment	deceased_indicator	default	owns_car	tenure'

pie = text.split(' ')
print(list(text))