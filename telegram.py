import os
from sys import executable
from time import sleep
import datetime

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup


TOKEN = "811923269:AAEvsabOZP_KFjVTUzF5Lr837IgK-kFyH-s"
admin_usernames = ("taskforce1", "VladislavChernyakoff")
filename = "logs.log"

def setup_proxy_and_start(token, proxy=True):
    # Указываем настройки прокси (socks5)
    address = "aws.komarov.ml"
    port = 1080
    username = "yandexlyceum"
    password = "yandex"

    # Создаем объект updater. В случае отсутствия пакета PySocks установим его
    try:

        updater = Updater(token, request_kwargs={'proxy_url': f'socks5://{address}:{port}/',
                                                 'urllib3_proxy_kwargs': {'username': username,
                                                                          'password': password}} if proxy else None)
        print('Proxy - OK!')

        # Запускаем бота
        main(updater)
    except RuntimeError:
        sleep(1)
        print('PySocks не установлен!')
        os.system(f'{executable} -m pip install pysocks --user')  # pip.main() не работает в pip 10.0.1

        print('\nЗавистимости установлены!\nПерезапустите бота!')
        exit(0)

def send_logs(bot, update):
    message = update.message.text
    if message == "Отправить последний лог":
        with open(filename, mode= "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            logs = lines[-1]
            update.message.reply_text(logs)

    elif message == "Отправить всю историю логов":
        with open(filename, mode= "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            logs = "\n".join([i for i in lines])
            update.message.reply_text(logs)

    elif message == "Отправить историю логов за сегодняшний день":
        with open(filename, mode= "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            date = str(datetime.datetime.now()).split(" ")[0]
            for i in lines:
                if date in i:
                    update.message.reply_text(i)

    elif message == "Отправить историю логов за последнюю неделю":
        with open(filename, mode="r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            date = datetime.datetime.now()
            dates_list = []
            for i in range(8):
                new_date = str(date - datetime.timedelta(i)).split(" ")[0]
                for j in lines:
                    if new_date in j:
                        dates_list.append(j)
            update.message.reply_text("\n".join([i for i in dates_list]))

    elif message == "Помощь":
        update.message.reply_text(
            "Используя бота вы можете просмотреть логи навыка 'Книга в Ухе' для Алисы ")
        update.message.reply_text("Для того чтобы посмотреть всю историю логов "
                                  "напишите 'Отправить всю историю логов'")
        update.message.reply_text("Для того чтобы посмотреть историю логов за последнюю неделю "
                                  "напишите 'Отправить историю логов за последнюю неделю'")
        update.message.reply_text("Для того чтобы посмотреть историю логов за сегодняшний день "
                                  "напишите 'Отправить историю логов за сегодняшний день'")
        update.message.reply_text("Для того чтобы посмотреть последний лог "
                                  "напишите 'Отправить последний лог'")


def start(bot, update):
    username = update.message.from_user.username
    if username in admin_usernames:
        reply_keyboard = [['Отправить всю историю логов', 'Отправить историю логов за последнюю неделю'],
                          ['Отправить историю логов за сегодняшний день', 'Отправить последний лог', 'Помощь']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(
            "Привет! Я бот, который осуществляет логирование навыка для Яндекс.Алисы 'Книга В Ухе''""!",
            reply_markup=markup)
    else:
        update.message.reply_text("Для того чтобы пользоваться данным ботом нужно обладать правами администратора.")


def main(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    text_handler = MessageHandler(Filters.text, send_logs)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # main()
    setup_proxy_and_start(token=TOKEN, proxy=True)