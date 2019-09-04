# uncompyle6 version 3.4.0
# Python bytecode 3.6 (3379)
# Decompiled from: Python 2.7.15+ (default, Nov 27 2018, 23:36:35) 
# [GCC 7.3.0]
# Embedded file name: /mnt/comun/pycharm-workspace/biwenger-bot/test.py
# Compiled at: 2019-09-04 19:16:03
# Size of source mod 2**32: 13148 bytes
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
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import requests, re
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=(logging.INFO))
logger = logging.getLogger(__name__)
CHOOSING, USERNAME_CHOICE, PASSWORD_CHOICE, MARKET_CHOICE, MARKET_APPLY = range(5)
start_reply_keyboard = [
 [
  'Login'], ['Salir']]
start_markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=True)
reply_keyboard = [
 [
  'Actualizar tus jugadores en el mercado'],
 [
  'Salir']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
percentage_reply_keyboard = [
 [
  '1'], ['50'], ['80'], ['100'], ['200']]
percentage_markup = ReplyKeyboardMarkup(percentage_reply_keyboard, one_time_keyboard=True)
url_login = 'https://biwenger.as.com/api/v2/auth/login'
url_account = 'https://biwenger.as.com/api/v2/account'
url_players_market = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
url_players_league = 'https://biwenger.as.com/api/v2/players/la-liga/'
url_retire_market = 'https://biwenger.as.com/api/v2/market?player='
url_add_player_market = 'https://biwenger.as.com/api/v2/market'
username = ''
password = ''
token = ''
percentage = 1

def start(update, context):
    """Send a message when the command /start is issued."""
    global password
    global username
    logger.info('llamada a start')
    if username == '':
        if password == '':
            update.message.reply_text('Hola! este bot permite agilizar acciones repetitivas en Biwenger.\nEnvia /Salir para salir.\nEnvia /help para recibir ayuda.\nDebes hacer Login primero para poder realizar acciones.\nQue quieres hacer?',
              reply_markup=start_markup)
        update.message.reply_text('Que quieres hacer ahora?',
          reply_markup=markup)
    return CHOOSING


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/start para empezar\n/Salir para finalizar')


def login_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text('Este es el proceso de login.\nDime tu username de biwenger:')
    return USERNAME_CHOICE


def username_choice(update, context):
    global username
    username = update.message.text
    context.user_data['choice'] = username
    logger.info('username: ' + username)
    update.message.reply_text('Dime tu password de biwenger:')
    return PASSWORD_CHOICE


def password_choice(update, context):
    global password
    global token
    password = update.message.text
    logger.info('password: ' + password)
    context.user_data['choice'] = password
    token = login(username, password)
    logger.info('token: ' + token)
    if 'error' in token:
        update.message.reply_text('Error en proceso login!',
          reply_markup=start_markup)
    else:
        update.message.reply_text('Login correcto!\nQue quieres hacer?',
          reply_markup=markup)
    return CHOOSING


def market_choice(update, context):
    update.message.reply_text('Indica el % a sumar al valor actual de los jugadores:', reply_markup=percentage_markup)
    return MARKET_APPLY


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text('Hasta otra!')
    user_data.clear()
    return ConversationHandler.END


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def market_apply(update, context):
    global percentage
    percentage = update.message.text
    logger.info('percentage: ' + percentage)
    context.user_data['choice'] = percentage
    logger.info('Renovar judgadores mercado')
    account_info = account(token)
    logger.info('contents: ' + repr(account_info))
    id_account = account_info['data']['account']['id']
    logger.info('id: ' + repr(id_account))
    id_league = account_info['data']['leagues'][0]['id']
    logger.info('league: ' + repr(id_league))
    id_user = account_info['data']['leagues'][0]['user']['id']
    logger.info('user: ' + repr(id_user))
    players_info = players(token, id_league, id_user)
    logger.info('list players info: ' + repr(players_info))
    if 'error' in players_info:
        logger.info('error calling list_players!' + players_info)
    else:
        pr_status = ''
        players_market = players_info['data']['market']
        logger.info('list players market: ' + repr(players_market))
        list_players = players_info['data']['players']
        logger.info('list players: ' + repr(list_players))
        logger.info('--actions with players info--')
        for player in list_players:
            auth = 'Bearer ' + token
            headers = {'Content-type':'application/json',  'Accept':'application/json, text/plain, */*',  'X-Lang':'es', 
             'X-League':repr(id_league),  'X-User':repr(id_user),  'Authorization':auth}
            player_info = requests.get((url_players_league + repr(player['id'])), headers=headers).json()['data']
            logger.info('name: ' + player_info['name'] + '; price=' + repr(player_info['price']))
            if is_player_in_market(player['id'], players_market):
                result = requests.delete((url_retire_market + repr(player['id'])), headers=headers)
                logger.info('result delete: ' + repr(result))
                data_add = {'type':'sell', 
                 'player':repr(player['id']),  'price':repr(int(player_info['price'] + player_info['price'] * int(percentage) / 100))}
                result = requests.post(url_add_player_market, data=(json.dumps(data_add)), headers=headers)
                logger.info('result player in market: ' + repr(result))
            else:
                data_add = {'type':'sell', 
                 'player':repr(player['id']),  'price':repr(int(player_info['price'] + player_info['price'] * int(percentage) / 100))}
                result = requests.post(url_add_player_market, data=(json.dumps(data_add)), headers=headers)
                logger.info('result player: ' + repr(result))
            if result.status_code == 200 or result.status_code == 204:
                logger.info('call ok!')
            else:
                logger.info('error in call, status: ' + str(result.status_code))
                pr_status = 'error'
                break

    if 'error' in pr_status:
        update.message.reply_text('Error en proceso update jugadores de mercado!',
          reply_markup=start_markup)
    else:
        update.message.reply_text('Jugadores actualizados en el mercado!',
          reply_markup=markup)
    return CHOOSING


def login(username, password):
    logger.info('Login process')
    data = {'email':username,  'password':password}
    headers = {'Content-type':'application/json',  'Accept':'application/json, text/plain, */*'}
    contents = requests.post(url_login, data=(json.dumps(data)), headers=headers).json()
    logger.info('contents: ' + repr(contents))
    if 'token' in contents:
        logger.info('call login ok!')
        return contents['token']
    else:
        logger.info('error in login call, status: ' + repr(contents['status']))
        return 'error, status' + repr(contents['status'])


def account(token):
    auth = 'Bearer ' + token
    headers = {'Content-type':'application/json',  'Accept':'application/json, text/plain, */*',  'X-Lang':'es',  'Authorization':auth}
    result = requests.get(url_account, headers=headers).json()
    if result['status'] == 200:
        logger.info('call login ok!')
        return result
    else:
        logger.info('error in account call, status: ' + str(result['status']))
        return 'error, status' + str(result['status'])


def players(token, league, user):
    auth = 'Bearer ' + token
    headers = {'Content-type':'application/json',  'Accept':'application/json, text/plain, */*',  'X-Lang':'es',  'X-League':repr(league), 
     'X-User':repr(user),  'Authorization':auth}
    result = requests.get(url_players_market, headers=headers).json()
    if result['status'] == 200:
        logger.info('call login ok!')
        return result
    else:
        logger.info('error in account call, result: ' + str(result))
        return 'error, status' + str(result['status'])


def is_player_in_market(id_player, players_market):
    player_in_market = False
    for player_market in players_market:
        if id_player == player_market['playerID']:
            return True


def main():
    """Start the bot."""
    updater = Updater('779706086:AAG2mU4alzP-s3_4RYGjOPAHTKwSsKkgCn0', use_context=True)
    username = ''
    password = ''
    dp = updater.dispatcher
    conv_handler = ConversationHandler(entry_points=[
     CommandHandler('start', start)],
      states={CHOOSING: [
                MessageHandler(Filters.regex('^(Login)$'), login_choice),
                MessageHandler(Filters.regex('^(Actualizar tus jugadores en el mercado)$'), market_choice)], 
     
     USERNAME_CHOICE: [
                       MessageHandler(Filters.text, username_choice)], 
     
     PASSWORD_CHOICE: [
                       MessageHandler(Filters.text, password_choice)], 
     
     MARKET_CHOICE: [
                     MessageHandler(Filters.text, market_choice)], 
     
     MARKET_APPLY: [
                    MessageHandler(Filters.text, market_apply)]},
      fallbacks=[
     MessageHandler(Filters.regex('^Salir$'), done)])
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
# okay decompiling test.cpython-36.pyc
