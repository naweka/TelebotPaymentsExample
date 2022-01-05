class HistoryElement(object):
	# Модель одного элемента для истории. Хранит в себе все необходимое:
	# данные телеграмма, крайний срок отправки платежа, комментарий, по которому будет производиться
	# поиск, сумма платежа
    def __init__(self, telegram_id, date_deadline, comment, summ):
        self.telegram_id, self.date_deadline, self.ready, self.comment, self.summ = telegram_id, date_deadline, False, comment, summ

    def __str__(self):
        return f'Крайний срок: {self.date_deadline}\nТребуемый комментарий: {self.comment}\nТребуемая сумма: {self.summ}'