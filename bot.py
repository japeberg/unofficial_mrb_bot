# scrapper.py

from lxml import html
import requests
import pickle
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import logging
import config


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
    pickle.dump(sent_messages, open(config.MESSAGES_PICKLE_FILEPATH, "wb"))

    ## ugly hack to get thread safety
    pickle.dump(chat_ids, open(config.CHAT_IDS_PICKLE_FILEPATH, "wb"))
    return unsent_messages


def callback_minute(context: telegram.ext.CallbackContext):
    urgent_messages = get_urgent_messages()
    if len(urgent_messages) != 0:
        for chat_id in chat_ids:
            message_to_send = "\n".join(urgent_messages)
            context.bot.send_message(chat_id=chat_id, text=message_to_send)


def start(update, context):
    chat_id_to_add = update.message.chat_id
    if chat_id_to_add not in chat_ids:
        chat_ids.append(chat_id_to_add)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Sie haben jetzt die Akutmeldungen der Mitteldeutschen Regiobahn abonniert.")
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Sie können das Abonnement jederzeit mit /stop beenden.")
        logging.info('new user succesfully subscribed')
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Sie haben die Akutmeldungen der Mitteldeutschen Regiobahn bereits abonniert.")
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Sie können das Abonnement jederzeit mit /stop beenden.")


def stop(update, context):
    chat_id_to_remove = update.message.chat_id
    if chat_id_to_remove not in chat_ids:
        context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben die Meldungen bereits deabonniert.")
    else:
        chat_ids.remove(update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben alle Meldungen deabonniert.")
        logging.info('user succesfully unsubscribed')


def unknown_command(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Ich kenne diesen Befehl nicht. Sie können den Dienst mit /start starten und mit /stop beenden.")


def unknown_rest(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Ich kann diese Nachricht nicht verstehen. Sie können den Dienst mit /start starten und mit /stop beenden.")
    logging.info(' UNKNOWN COMMAND FROM USER: "' + update.message.text + '"')

logging.basicConfig(filename=config.LOGS_FILEPATH, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    sent_messages = pickle.load(open(config.MESSAGES_PICKLE_FILEPATH, "rb"))
except FileNotFoundError:
    sent_messages = list()

try:
    chat_ids = pickle.load(open(config.CHAT_IDS_PICKLE_FILEPATH, "rb"))
except FileNotFoundError:
    chat_ids = list()


updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)



unknown_command_handler = MessageHandler(Filters.command, unknown_command)
dispatcher.add_handler(unknown_command_handler)

unknown_rest_handler = MessageHandler(Filters.all, unknown_rest)
dispatcher.add_handler(unknown_rest_handler)

j = updater.job_queue
job_minute = j.run_repeating(callback_minute, interval=60, first=0)

updater.start_polling()
