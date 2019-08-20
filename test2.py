#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging, requests, re, json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    logger.info("Holaaa!!!")
    url = 'https://biwenger.as.com/api/v2/auth/login'
    data = {"email": "xusmen69@gmail.com","password":"xX22021983b"}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*'}
    contents = requests.post(url,data=json.dumps(data), headers=headers).json()
    logger.info("contents: " + repr(contents))
    token = contents['token']
    logger.info("token: " + token)

    url = 'https://biwenger.as.com/api/v2/account'
    auth = 'Bearer ' + token
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'X-Lang': 'es', 'Authorization': auth}
    account = requests.get(url, headers=headers).json()
    logger.info("contents: " + repr(account))
    id = account['data']['account']['id']
    logger.info("id: " + repr(id))
    league = account['data']['leagues'][0]['id']
    logger.info("league: " + repr(league))
    user = account['data']['leagues'][0]['user']['id']
    logger.info("user: " + repr(user))

    url = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
    auth = 'Bearer ' + token
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'X-Lang': 'es', 'X-League': repr(league), 'X-User': repr(user), 'Authorization': auth}
    listajug = requests.get(url, headers=headers).json()
    logger.info("lista: " + repr(listajug))


if __name__ == '__main__':
    main()
