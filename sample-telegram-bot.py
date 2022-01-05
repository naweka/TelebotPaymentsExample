import telebot
from os.path import isfile
import requests
import json
import datetime
import hashlib
import threading
import time

from history_element import HistoryElement
from save_load import save_data, load_data
from thread import Thread

telegram_token = ''

my_login = ''
qiwi_token = ''
qiwi_nick = ''

lock = threading.Lock()
bot = telebot.TeleBot(telegram_token)
history = load_data('data.txt') if isfile('data.txt') else []


def clear_dead_requests():
    global history
    time_now = datetime.datetime.now()
    temp_history = []

    with lock:
        for elem in history:
            if elem.date_deadline > time_now:
                temp_history.append(elem)
            else:
                print(f'Истек срок платежа:\n{elem}\nПлатеж был совершен:{elem.ready}')
                if not elem.ready:
                    bot.send_message(elem.telegram_id, f'Истек срок платежа!')
        history = temp_history


def thread_history_handler():
    global history
    while True:
        time.sleep(10)
        print('\nОчистка истории...')
        clear_dead_requests()
        print('Сбор и обработка платежей...')
        # Получаем историю платежей (10 штук)
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + qiwi_token
        parameters = {'rows': '10'}
        h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + my_login + '/payments', params=parameters)
        json_obj = json.loads(h.text)

        # Перебираем все содержимое и сравниваем с тем, что нам нужно
        with lock:
            for history_elem in history:
                for i in range(10):
                    # Если комментарий тот, сумма та же (или больше) и этот платеж еще не был обработан, то
                    # отправляем юзеру уведомление и помечаем платеж
                    if history_elem.comment == json_obj['data'][i]['comment'] and history_elem.summ <= \
                            json_obj['data'][i]['sum']['amount'] and not history_elem.ready:
                        print(f'Платеж прошел успешно!\n{history_elem}')
                        history_elem.ready = True
                        bot.send_message(history_elem.telegram_id, f'Оплата прошла успешно!')
        save_data('data.txt', history)
        print('Готово')


# Фунция, отвечающая за команду /test
@bot.message_handler(commands=['test'])
def test_command(message):
    global history
    time_now = datetime.datetime.now()
    # Формируем крайний срок оплаты (+ 15 минут)
    time_deadline = time_now + datetime.timedelta(minutes=15)
    # Формируем стоимость платежа
    summ = 30
    # Формируем код для комментария
    comment = hashlib.sha224(str(time_deadline).encode('utf-8')).hexdigest()[:6]

    hist_elem = HistoryElement(message.chat.id, time_deadline, comment, summ)
    history.append(hist_elem)
    save_data('data.txt', history)

    bot.send_message(message.chat.id,
                     f'Отправьте указанную сумму на киви кошелек по никнейму "{qiwi_nick}".\nИнформация по заказу:\n\n {hist_elem} \nБот отправит ваш заказ автоматически')


# Запускаем в отдельном потоке чекер платежей
history_handler = Thread(thread_history_handler)

print('Бот запускается...')
bot.infinity_polling()
