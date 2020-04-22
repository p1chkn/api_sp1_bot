'''
Бот крутиться на серверах Heroku, @pl_chkn_bot его имя в телеграме
'''
import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):

    homework_name = homework['homework_name']
    status = homework['status']
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    params = {
        'from_date': current_timestamp
             }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    homework_statuses = requests.get(url=url, headers=headers, params=params)
    return homework_statuses.json()


def get_updates():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': None}
    return requests.get(url=url, params=params).json()['result']


def get_last_update():
    get_result = get_updates()
    if len(get_result) > 0:
        last_update = get_result[-1]
    else:
        last_update = get_result[len(get_result)]
    return last_update


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


'''
К сожалению, из-за тестов нельзя ввести еще один параметр в функцию отправки сообщений :(
поэтому сообщения не себе приходится довольно некрасиво отправлять
'''


def main():
    current_timestamp = int(time.time())
    update = get_last_update()
    send_message('Hi! start working!')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            if (int(time.time())-current_timestamp) > 900:
                new_homework = get_homework_statuses(current_timestamp)
                current_timestamp = new_homework.get('current_date')
            if new_homework.get('homeworks'):
                for item in new_homework.get('homeworks'):
                    send_message(parse_homework_status(item))
                current_timestamp = new_homework.get('current_date')
            if update != get_last_update():
                update = get_last_update()
                name = update['message']['from']['first_name']
                chat_id = update['message']['from']['id']
                if chat_id == CHAT_ID:
                    send_message('Привет, хозяин!')
                else:
                    message = f'Привет, {name}! Я бот-ассистент Павла!'
                    bot.send_message(chat_id=chat_id, text=message)
            time.sleep(3)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':

    main()
