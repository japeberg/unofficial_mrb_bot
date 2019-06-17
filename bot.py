# scrapper.py

from lxml import html
import requests
import pickle
import telegram
from telegram.ext import Updater
import logging
import config
from telegram.ext import CommandHandler


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
            reason = str(message[2])
            alternatives = str(message[3])
            message_to_send = title + "  " + url + "\n" + text + "" + reason + "" + alternatives
            if message_to_send not in sent_messages:
                unsent_messages.append(message_to_send)
                sent_messages.append(message_to_send)
    pickle.dump(sent_messages, open(config.MESSAGES_PICKLE_FILEPATH, "wb"))
    return unsent_messages


def callback_minute(context: telegram.ext.CallbackContext):
    for chat_id in chat_ids:
        message_to_send = "\n".join(get_urgent_messages())
        context.bot.send_message(chat_id=chat_id, text=message_to_send)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben jetzt die Akutmeldungen der Mitteldeutschen Regiobahn abonniert")
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie können das Abonnement jederzeit mit /stop beenden")
    chat_ids.append(update.message.chat_id)
    pickle.dump(chat_ids, open(config.CHAT_IDS_PICKLE_FILEPATH, "wb"))


def stop(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Sie haben alle Meldungen deabonniert")
    chat_ids.remove(update.message.chat_id)
    pickle.dump(chat_ids, open(config.CHAT_IDS_PICKLE_FILEPATH, "wb"))


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

j = updater.job_queue
job_minute = j.run_repeating(callback_minute, interval=60, first=0)
updater.start_polling()
