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


def send_message(message, chat_id=CHAT_ID):
    #proxy = telegram.utils.request.Request(
    #    proxy_url='socks5://104.248.63.15:30588')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    update = get_last_update()
    send_message('Hi!')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                for item in new_homework.get('homeworks'):
                    send_message(parse_homework_status(item))
                current_timestamp = new_homework.get('current_date')
            if update != get_last_update():
                update = get_last_update()
                name = update['message']['from']['first_name']
                chat_id = update['message']['from']['id']
                if chat_id == 214179795:
                    send_message('Привет, хозяин!')
                else:
                    send_message(f'Привет, {name}! Я бот-ассистент Павла!', chat_id=chat_id)
            time.sleep(3)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':

    main()
