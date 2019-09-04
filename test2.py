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
url_login = 'https://biwenger.as.com/api/v2/auth/login'
url_account = 'https://biwenger.as.com/api/v2/account'
url_players_market = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
url_players_league = 'https://biwenger.as.com/api/v2/players/la-liga/'
url_retire_market = "https://biwenger.as.com/api/v2/market?player="
url_add_player_market = "https://biwenger.as.com/api/v2/market"


def main():
    username = "S"
    password = ""
    percentage = 80

    # login process
    token = login(username, password)
    logger.info("token: " + token)

    # getting account info needed to the future calls headers
    account_info = account(token)
    logger.info("contents: " + repr(account_info))
    id_account = account_info['data']['account']['id']
    logger.info("id: " + repr(id_account))
    id_league = account_info['data']['leagues'][0]['id']
    logger.info("league: " + repr(id_league))
    id_user = account_info['data']['leagues'][0]['user']['id']
    logger.info("user: " + repr(id_user))

    # get player info
    players_info = players(token, id_league, id_user)
    logger.info("list players info: " + repr(players_info))

    if "error" in players_info:
        logger.info("error calling list_players!" + players_info)
    else:
        players_market = players_info['data']['market']
        logger.info("list players market: " + repr(players_market))
        list_players = players_info['data']['players']
        logger.info("list players: " + repr(list_players))

        logger.info("--actions with players info--")
        # get and set players into market
        for player in list_players:
            auth = 'Bearer ' + token
            headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*',
                       'X-Lang': 'es', 'X-League': repr(id_league), 'X-User': repr(id_user), 'Authorization': auth}
            player_info = requests.get(url_players_league + repr(player['id']), headers=headers).json()['data']
            logger.info("name: " + player_info['name'] + "; price=" + repr(
                player_info['price']))
            if is_player_in_market(player['id'], players_market):
                # logger.info("jugador: " + repr(jugador['id']) + " ;precio real:" + repr(jugador["owner"]["price"]) + " ;precio mercado:" + repr(jugadorMercado["price"]))
                result = requests.delete(url_retire_market + repr(player['id']), headers=headers)
                logger.info("result delete: " + repr(result))

                data_add = {"type": "sell", "player": repr(player['id']),
                            "price": repr(int(player_info['price'] + ((player_info['price'] * percentage) / 100)))}
                result = requests.post(url_add_player_market, data=json.dumps(data_add), headers=headers)
                logger.info("result player in market: " + repr(result))
            else:
                data_add = {"type": "sell", "player": repr(player['id']),
                            "price": repr(int(player_info['price'] + ((player_info['price'] * percentage) / 100)))}
                result = requests.post(url_add_player_market, data=json.dumps(data_add), headers=headers)
                logger.info("result player: " + repr(result))

            if result['status'] == 200 or result['status'] == 204:
                logger.info("call ok!")
            else:
                logger.info("error in call, staus: " + str(result['status']))
                break


def login(username, password):
    logger.info("Login process")
    data = {"email": username, "password": password}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*'}
    contents = requests.post(url_login, data=json.dumps(data), headers=headers).json()
    logger.info("contents: " + repr(contents))
    if "token" in contents:
        logger.info("call login ok!")
        return contents['token']
    else:
        logger.info("error in login call, status: " + contents['status'])
        return "error, status" + contents['status']


def account(token):
    auth = 'Bearer ' + token
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'X-Lang': 'es',
               'Authorization': auth}
    result = requests.get(url_account, headers=headers).json()
    if result['status'] == 200:
        logger.info("call login ok!")
        return result
    else:
        logger.info("error in account call, status: " + str(result['status']))
        return "error, status" + str(result['status'])


def players(token, league, user):
    auth = 'Bearer ' + token
    headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'X-Lang': 'es',
               'X-League': repr(league), 'X-User': repr(user), 'Authorization': auth}
    result = requests.get(url_players_market, headers=headers).json()
    if result['status'] == 200:
        logger.info("call login ok!")
        return result
    else:
        logger.info("error in account call, result: " + str(result))
        return "error, status" + str(result['status'])


def is_player_in_market(id_player, players_market):
    player_in_market = False
    for player_market in players_market:
        if id_player == player_market['playerID']:
            return True
            break


if __name__ == '__main__':
    main()
