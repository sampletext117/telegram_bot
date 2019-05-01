import os
from sys import executable
from time import sleep
import datetime
import json
import requests

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup

TOKEN = "811923269:AAEvsabOZP_KFjVTUzF5Lr837IgK-kFyH-s"
admin_usernames = ("taskforce1", "VladislavChernyakoff", "FarmArt", "lapevgen")
filename = "logs.log"


def setup_proxy_and_start(token, proxy=True):
    # Указываем настройки прокси (socks5)
    address = "aws.komarov.ml"
    port = 1080
    username = "yandexlyceum"
    password = "yandex"

    try:

        updater = Updater(
            token,
            request_kwargs={
                'proxy_url': f'socks5://{address}:{port}/',
                'urllib3_proxy_kwargs': {
                    'username': username,
                    'password': password}} if proxy else None)
        print('Proxy - OK!')
        main(updater)

    except RuntimeError:
        sleep(1)
        print('PySocks не установлен!')
        # pip.main() не работает в pip 10.0.1
        os.system(f'{executable} -m pip install pysocks --user')

        print('\nЗавистимости установлены!\nПерезапустите бота!')
        exit(0)


def get_logs():
    url = "https://audiobook-alisa.herokuapp.com/logs"
    key = "pbkdf2:sha256:150000$IClecKJx$40bfa7b4f7cbaa132c1755527fca3fcb73093d15bc1a56bab80c7433873e79ac"
    dict_key = {'key': key}
    json_key = json.dumps(dict_key, ensure_ascii=False)
    response = requests.post(url, json=json_key)
    json_response = response.json()
    logs = json_response['logs'].split("\n")
    return logs


def clear_logs():
    url = "https://audiobook-alisa.herokuapp.com/clear_logs"
    key = "pbkdf2:sha256:150000$IClecKJx$40bfa7b4f7cbaa132c1755527fca3fcb73093d15bc1a56bab80c7433873e79ac"
    dict_key = {'key': key}
    json_key = json.dumps(dict_key, ensure_ascii=False)
    response = requests.post(url, json=json_key)
    json_response = response.json()
    result = json_response['result']
    return result


def send_logs(bot, update):
    username = update.message.from_user.username
    if username in admin_usernames:
        message = update.message.text
        all_logs = get_logs()
        if message == "Отправить последний лог":
            logs = all_logs[-2]
            update.message.reply_text(logs)

        elif message == "Отправить всю историю логов":
            logs = "\n".join([i for i in all_logs])
            update.message.reply_text(logs)

        elif message == "Отправить историю логов за сегодняшний день":
            date = str(datetime.datetime.now()).split(" ")[0]
            logs_list = []
            for i in all_logs:
                if date in i.split(" ")[0]:
                    logs_list.append(i)
            update.message.reply_text("\n".join([i for i in logs_list]))

        elif message == "Отправить историю логов за последнюю неделю":
            date = datetime.datetime.now()
            dates_list = []
            for i in range(8):
                new_date = str(date - datetime.timedelta(i)).split(" ")[0]
                for j in all_logs:
                    if new_date in j:
                        dates_list.append(j)
            update.message.reply_text("\n".join([i for i in dates_list]))

        elif message == "Очистить историю логов":
            result = clear_logs()
            if result == 'success':
                update.message.reply_text("История логов очищена")
            else:
                update.message.reply_text(
                    "Неизвестная ошибка: не получилось очистить историю логов")

        elif message == "Помощь":
            update.message.reply_text(
                "Используя бота вы можете просмотреть логи навыка 'Книга в Ухе' для Алисы ")
            update.message.reply_text(
                "Для того, чтобы посмотреть всю историю логов, "
                "напишите 'Отправить всю историю логов'")
            update.message.reply_text(
                "Для того, чтобы посмотреть историю логов за последнюю неделю, "
                "напишите 'Отправить историю логов за последнюю неделю'")
            update.message.reply_text(
                "Для того, чтобы посмотреть историю логов за сегодняшний день, "
                "напишите 'Отправить историю логов за сегодняшний день'")
            update.message.reply_text(
                "Для того, чтобы посмотреть последний лог, "
                "напишите 'Отправить последний лог'")
            update.message.reply_text(
                "Для того, чтобы очистить всю историю логов, "
                "напишите 'Очистить историю логов'")
        else:
            update.message.reply_text(
                "Не понял вашу команду. Чтобы просмотреть список возможных действий, напишите 'Помощь'")
    else:
        update.message.reply_text(
            "А ну иди сюда юзверь собачий я у тебя сам логи попрошу бухгалтерша чёртова. "
            "Я же сказал без админки тебе, существо ты непонятливое, здесь делать нечего.")


def start(bot, update):
    username = update.message.from_user.username
    if username in admin_usernames:
        reply_keyboard = [['Помощь', 'Отправить всю историю логов',
                           'Отправить историю логов за последнюю неделю'],
                          ['Отправить историю логов за сегодняшний день',
                           'Отправить последний лог',
                           'Очистить историю логов']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(
            "Привет! Я бот, который осуществляет логирование навыка для Яндекс.Алисы 'Книга В Ухе''"
            "!", reply_markup=markup)
    else:
        update.message.reply_text(
            "Для того, чтобы пользоваться данным ботом, нужно обладать правами администратора.")


def main(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    text_handler = MessageHandler(Filters.text, send_logs)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_proxy_and_start(token=TOKEN, proxy=True)
