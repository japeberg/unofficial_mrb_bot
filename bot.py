# scrapper.py

from lxml import html
import requests
import telegram
from telegram import  InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import logging
import config
import signal
import sys
import sqlite3
import data_structures
from datetime import datetime

data_structures.Session

# def build_menu(buttons,
#                n_cols,
#                header_buttons=None,
#                footer_buttons=None):
#     menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
#     if header_buttons:
#         menu.insert(0, [header_buttons])
#     if footer_buttons:
#         menu.append([footer_buttons])
#     return menu
#
#
# def button(update, context):
#     query = update.callback_query
#
#     query.edit_message_text(text="Selected option: {}".format(query.data))
#
# def menu(update, context):
#     # button_list = [
#     #     InlineKeyboardButton("RE6", callback_data="RE6"),
#     #     InlineKeyboardButton("RB30", callback_data="RB30"),
#     #     InlineKeyboardButton("RB 110", callback_data="RB 110")
#     # ]
#     dict_of_buttons = {"test": "test_test",
#                        "test2": "test_test_test"}
#     some_strings = ["col1", "col2", "row2"]
#     button_list = [[KeyboardButton(s)] for s in dict_of_buttons]
#     reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
#     context.bot.send_message(update.message.chat_id, "Welche Linie wollen sie abonnieren?", reply_markup=reply_markup)

def get_urgent_messages():
    urls_to_parse = {
        'RE 6':'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-6-leipzig-chemnitz',
        'RE 3':'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-3-dresden-hof',
        'RB 30':'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-30-dresden-zwickau',
        'RB 45':'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-45-chemnitz-elsterwerda',
        'RB 110':'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-110-leipzig-hbf-doebeln-hbf'
    }
    unsent_messages = list()

    for url in urls_to_parse:
        line_site = requests.get(url=urls_to_parse[url])
        site_content = line_site.content.decode("utf-8")
        tree = html.fromstring(site_content)

        urgent_messages = tree.xpath('//div[@class="urgent-reports__text"]')
        for idx in range(0, len(urgent_messages)):
            message = urgent_messages[idx].xpath('p/text()')
            title = str(message[0])
            text = str(message[1])
            try:
                reason = str(message[2])
            except IndexError:
                reason = ""
            try:
                alternatives = str(message[3])
            except IndexError:
                alternatives = ""
            message_to_send = title + "  " + "\n" + url + " - " + text + reason + alternatives + "\n"
            if message_to_send not in sent_messages:
                unsent_messages.append(message_to_send)
                sent_messages.append(message_to_send)
    return unsent_messages




def callback_minute(context: telegram.ext.CallbackContext):
    urgent_messages = get_urgent_messages()
    db_conn = sqlite3.connect(config.SQLITE_DB)
    if len(urgent_messages) != 0:
        for chat_id in chat_ids:
            message_to_send = "\n".join(urgent_messages)
            context.bot.send_message(chat_id=chat_id, text=message_to_send)
            save_sent_message_to_table(message_to_send, db_conn)

    db_conn.close()

def start(update, context):
    session = data_structures.Session()
    chat_id_to_add = update.message.chat_id
    # if chat_id_to_add not in chat_ids:
    #     chat_ids.append(chat_id_to_add)
    #     save_id_to_table(chat_id_to_add, db_conn)
    #     context.bot.send_message(chat_id=update.message.chat_id,
    #                              text="Sie haben jetzt die Akutmeldungen der Mitteldeutschen Regiobahn abonniert.")
    #     context.bot.send_message(chat_id=update.message.chat_id,
    #                              text="Sie können das Abonnement jederzeit mit /stop beenden.")
    #     logging.info('new user succesfully subscribed')
    # else:
    #     context.bot.send_message(chat_id=update.message.chat_id,
    #                              text="Sie haben die Akutmeldungen der Mitteldeutschen Regiobahn bereits abonniert.")
    #     context.bot.send_message(chat_id=update.message.chat_id,
    #                              text="Sie können das Abonnement jederzeit mit /stop beenden.")
    new_subscriber = data_structures.subscriber(chat_id=chat_id_to_add, subscribed_on=datetime.now())
    session.add(new_subscriber)
    print(chat_id_to_add)
    session.commit()




def stop(update, context):
    db_conn = sqlite3.connect(config.SQLITE_DB)
    chat_id_to_remove = update.message.chat_id
    if chat_id_to_remove not in chat_ids:
        context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben die Meldungen bereits deabonniert.")
    else:
        chat_ids.remove(update.message.chat_id)
        delete_id_from_table(update.message.chat_id, db_conn)
        context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben alle Meldungen deabonniert.")
        logging.info('user succesfully unsubscribed')

    db_conn.close()


def unknown_command(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Ich kenne diesen Befehl nicht. Sie können den Dienst mit /start starten und mit /stop beenden.")


def unknown_rest(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Ich kann diese Nachricht nicht verstehen. Sie können den Dienst mit /start starten und mit /stop beenden.")
    logging.info(' UNKNOWN COMMAND FROM USER: "' + update.message.text + '"')


def handle_shutdown(signum=None, frame=None):
    logging.info('shutdown by SIGNAL ' + str(signum))
    sys.exit(1)

def create_table(tablename, db_connection):
    # TODO: Get table names and descriptions from constants or something
    cursor = db_connection.cursor()
    if (tablename == 'chat_ids'):
        cursor.execute("CREATE TABLE {0} (chat_ids text)".format(tablename))
    if (tablename == 'sent_messages'):
        cursor.execute("CREATE TABLE {0} (messages text)".format(tablename))

    db_connection.commit();

def save_id_to_table(chat_id, db_connection):
    cursor = db_connection.cursor()

    # TODO: Get table names and descriptions from constants or something
    # TODO: Remove all / Insert all == most efficient approach?
    existing_ids = cursor.execute('SELECT chat_ids FROM chat_ids WHERE chat_ids=?', (chat_id,)).fetchall()
    if len(existing_ids) == 0:
        cursor.execute('INSERT INTO chat_ids VALUES (?)', (chat_id,))

    db_connection.commit()

def delete_id_from_table(chat_id, db_connection):
    cursor = db_connection.cursor()

    # TODO: Get table names and descriptions from constants or something
    # TODO: Remove all / Insert all == most efficient approach?
    cursor.execute('DELETE FROM chat_ids WHERE chat_ids=?', (chat_id,))

    db_connection.commit()

def save_sent_message_to_table(sent_message, db_connection):
    cursor = db_connection.cursor()
    # TODO: Get table names and descriptions from constants or something
    # TODO: Remove all / Insert all == most efficient approach?
    cursor.execute('INSERT INTO sent_messages VALUES (?)', (sent_message,))


    db_connection.commit()

def init_db_if_new(db_connection):
    # TODO: Get table names and descriptions from constants or something
    cursor = db_connection.cursor()
    table_names = [('chat_ids'),('sent_messages')]
    string = 'SELECT name FROM sqlite_master WHERE type="table" AND name IN ' + ','.join('?'*len(table_names))
    result = cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name IN ('
                            + ','.join('?'*len(table_names))
                            + ')', table_names)
    existing_tables = []
    for row in result:
        existing_tables.append(row[0])

    for table_name in table_names:
        if(table_name not in existing_tables):
            create_table(table_name, db_connection)


logging.basicConfig(filename=config.LOGS_FILEPATH, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.info('started bot')

db_conn = sqlite3.connect(config.SQLITE_DB)
init_db_if_new(db_conn)
db_cursor = db_conn.cursor()

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

sent_messages = list()
try:
    # TODO: Get table names and descriptions from constants or something
    message_entries = db_cursor.execute('SELECT messages FROM sent_messages').fetchall()
    for entry in message_entries:
        sent_messages.append(entry[0])
except sqlite3.Error: # TODO: Lazy!
    logging.error("Error fetching sent_messages")

chat_ids = list()
try:
    # TODO: Get table names and descriptions from constants or something
    chat_id_entries = db_cursor.execute('SELECT chat_ids FROM chat_ids').fetchall()
    for entry in chat_id_entries:
        chat_ids.append(entry[0])
except sqlite3.Error: # TODO: Lazy!
    logging.error("Error fetching chat_ids")

db_conn.close()


updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
# updater.dispatcher.add_handler(CallbackQueryHandler(button))

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)

# menu_handler = CommandHandler('menu', menu)
# dispatcher.add_handler(menu_handler)
#


unknown_command_handler = MessageHandler(Filters.command, unknown_command)
dispatcher.add_handler(unknown_command_handler)

unknown_rest_handler = MessageHandler(Filters.all, unknown_rest)
dispatcher.add_handler(unknown_rest_handler)

j = updater.job_queue
job_minute = j.run_repeating(callback_minute, interval=60, first=0)

updater.start_polling()
