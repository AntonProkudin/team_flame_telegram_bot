import telebot
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from main import requestor, bot


class TaskHandler:
    @staticmethod
    def create_task(self, call: telebot.types.CallbackQuery):
        # Введите название задачи
        # Введите описание задачи

        print('Create Task')

    # Получить список всех задач и отобразить их
    @staticmethod
    def get_tasks(self, call: telebot.types.CallbackQuery):
        last_chat_id = call.message.chat.id
        last_message_id = call.message.id

        markup = InlineKeyboardMarkup()

        attached_tasks = requestor.get_user_task()

        for task in attached_tasks:
            markup.add(InlineKeyboardButton(f'Задача {task["name"]}', callback_data=f'task_details_{task["id"]}'))

        markup.add(InlineKeyboardButton(f'Создать задачу', callback_data=f'create_task'))
        markup.add(InlineKeyboardButton(f'Назад', callback_data=f'back'))

        bot.edit_message_text('Задачи:', last_chat_id, last_message_id, reply_markup=markup)

    # Получить информацию о конкретной задаче
    @staticmethod
    def get_task_details(self, call: telebot.types.CallbackQuery):
        last_chat_id = call.message.chat.id
        last_message_id = call.message.id

        markup = InlineKeyboardMarkup()

        task_id = call.data.split('_')[-1]

        task = requestor.get_task_by_id(task_id)

        markup.add(
            InlineKeyboardButton('Редактировать', callback_data=f'edit_task_{task_id}'),
            InlineKeyboardButton('Изменить статус', callback_data=f'change_status_{task["boardId"]}_{task["id"]}'),
            InlineKeyboardButton('Оставить комментарий', callback_data=f'add_comment_{task_id}'),
            InlineKeyboardButton('Назад', callback_data=f'tasks'),
        )

        task_priority = priority_map.get(task['priority'])

        task_priority = 'Отсутствует' if task_priority is None else task_priority

        bot.edit_message_text(
            f'Задача {task["name"]}\nОписание: {task["description"]}\nСоздатель: {task["creator"]["name"]}\nПриоритет '
            f'задачи: {task_priority}\nCтатус задачи: {task["status"]}',
            last_chat_id,
            last_message_id,
            reply_markup=markup)
