import re
import zlib

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo

from repository.requestor import Requestor
from resources import priority_map, status_map

bot = telebot.TeleBot("6677254983:AAEk-f2Q6aVOb2l_Z-wMfcUKYiJUES-R8gk", parse_mode=None)

json_access_token = {}

requestor = Requestor()


def search_commands(commands, command):
    for i in commands:

        if re.match(i, command):
            return i


def _set_user_email_and_password(message: telebot.types.Message):
    email = message.text.split(';')[0]
    password = message.text.split(';')[1]

    response = requestor.authorize_user(email, password)

    if response.status_code == 200:
        json_access_token[message.from_user.id] = response.json()['tokens']['accessToken']['token']

        requestor.set_header(json_access_token[message.from_user.id])

        _handle_start_command(message)

    else:

        print(response.status_code)

        print(response.json())

        bot.send_message(message.chat.id, 'Неправильный логин и/или пароль')


def _handle_start_command(message: telebot.types.Message):
    if json_access_token.get(message.from_user.id) is not None:

        requestor.set_header(json_access_token[message.from_user.id])

        markup = InlineKeyboardMarkup()
        markup.row_width = 3

        markup.add(InlineKeyboardButton("Задачи", callback_data="tasks"),
                   InlineKeyboardButton("Список команд", callback_data="commands"),
                   InlineKeyboardButton("Dashboard", callback_data="dashboard"))

        bot.send_message(message.chat.id, 'Набор команд:', reply_markup=markup)


    else:
        bot.send_message(message.chat.id, 'Введите логин и пароль пользователя в формате username;password')

        bot.register_next_step_handler(message, _set_user_email_and_password)


def _handle_back_request(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()
    markup.row_width = 3

    markup.add(InlineKeyboardButton("Задачи", callback_data="tasks"),
               InlineKeyboardButton("Список команд", callback_data="commands"),
               InlineKeyboardButton("Dashboard", callback_data="dashboard"))

    bot.edit_message_text('Набор команд:', last_chat_id, last_message_id, reply_markup=markup)


def _handle_tasks_request(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()

    attached_tasks = requestor.get_user_task()

    for task in attached_tasks:
        markup.add(InlineKeyboardButton(f'Задача {task["name"]}', callback_data=f'task_details_{task["id"]}'))

    markup.add(InlineKeyboardButton(f'Создать задачу', callback_data=f'create_task'))
    markup.add(InlineKeyboardButton(f'Назад', callback_data=f'back'))

    bot.edit_message_text('Задачи:', last_chat_id, last_message_id, reply_markup=markup)


def _handle_task_request(call: telebot.types.CallbackQuery):
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


def _set_description(message: telebot.types.Message, task_id: int):
    requestor.update_task(task_id, 'description', message.text)

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.send_message(message.chat.id, "Задача успешно обновлена", reply_markup=markup)


def _set_title(message: telebot.types.Message, task_id: int):
    requestor.update_task(task_id, 'name', message.text)

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.send_message(message.chat.id, "Введите новое описание задачи", reply_markup=markup)

    bot.register_next_step_handler(message, _set_description, task_id)


def _handle_edit_task_request(call: telebot.types.CallbackQuery):
    markup = InlineKeyboardMarkup()

    task_id = call.data.split('_')[-1]

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.send_message(call.message.chat.id, 'Введите новое название задачи', reply_markup=markup)

    bot.register_next_step_handler(call.message, _set_title, task_id)


def _handle_change_task_status(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()

    task_id = call.data.split('_')[-1]

    board_id = call.data.split('_')[-2]

    statuses = requestor.get_column_by_board_id(board_id)

    for status in statuses:
        callback_data = f'task_status_{status["id"]}_{task_id}'

        markup.add(InlineKeyboardButton(status['name'], callback_data=callback_data))

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.edit_message_text('Выберите статус задачи', last_chat_id, last_message_id, reply_markup=markup)


def _handle_task_status_change(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()

    task_id = call.data.split('_')[-1]

    column_id = call.data.split('_')[-2]

    requestor.change_task_status(task_id, column_id)

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.edit_message_text('Статус задачи успешно изменен', last_chat_id, last_message_id, reply_markup=markup)


def _set_comment(message: telebot.types.Message, task_id: int):
    requestor.create_comment(message.text, task_id=task_id)

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton('Назад', callback_data=f'task_details_{task_id}'))

    bot.send_message(message.chat.id, 'Комментарий успешно создан', reply_markup=markup)


def _handle_add_comment_request(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()

    task_id = call.data.split('_')[-1]

    bot.edit_message_text('Введите комментарий к задаче:', last_chat_id, last_message_id, reply_markup=markup)

    bot.register_next_step_handler(call.message, _set_comment, task_id)


def _input_title_and_description(message: telebot.types.Message):
    title = message.text.split(';')[0]

    description = message.text.split(';')[1]

    requestor.create_task(title, description)

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("Назад", callback_data="tasks"))

    bot.send_message(message.chat.id, 'Задача успешно создана', reply_markup=markup)


def _handle_create_task_request(call: telebot.types.CallbackQuery):
    last_chat_id = call.message.chat.id
    last_message_id = call.message.id

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("Назад", callback_data="tasks"))

    bot.edit_message_text('Введите название и описание задачи в следующем формате: Название;Описание', last_chat_id,
                          last_message_id, reply_markup=markup)

    bot.register_next_step_handler(call.message, _input_title_and_description)


command_list = {'/start': _handle_start_command}

callback_list = {

    'tasks': _handle_tasks_request,
    'task_details': _handle_task_request,
    'edit_task': _handle_edit_task_request,
    'create_task': _handle_create_task_request,
    'change_status': _handle_change_task_status,
    'task_status': _handle_task_status_change,
    'add_comment': _handle_add_comment_request,
    'back': _handle_back_request,
}


@bot.message_handler(func=lambda m: True)
def message_handler(message: telebot.types.Message):
    selected_command = command_list.get(message.text)

    if selected_command is not None:
        selected_command(message)


@bot.callback_query_handler(func=lambda call: True)
def query_callback_handler(call: telebot.types.CallbackQuery):
    selected_command = callback_list.get(call.data)

    if selected_command is None:
        selected_command = callback_list.get(search_commands(callback_list.keys(), call.data))

        if selected_command is not None:
            selected_command(call)

    else:
        selected_command(call)


bot.infinity_polling()
