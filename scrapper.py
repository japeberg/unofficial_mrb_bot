# scrapper.py

from lxml import html
import requests
import pickle
import time
import telegram
import config

bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)
url = 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-6-leipzig-chemnitz'


def get_and_send_urgent_messages():
    try:
        sent_messages = pickle.load(open("hashes.pickle", "rb"))
    except:
        sent_messages = list()

    line_site = requests.get(url=url)
    site_content = line_site.content.decode("utf-8")
    tree = html.fromstring(site_content)

    urgent_messages = tree.xpath('//div[@class="urgent-reports__text"]')
    for idx in range(0,len(urgent_messages)):
        message = urgent_messages[idx].xpath('p/text()')
        title = str(message[0])
        text = str(message[1])
        reason = str(message[2])
        alternatives = str(message[3])
        if text not in sent_messages:
            message_to_send = title + " (Linie RE 6) " + "\n\n" + text + "\n" + reason + "\n" + alternatives
            bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=message_to_send)
            sent_messages.append(text)
    pickle.dump(sent_messages, open("hashes.pickle", "wb"))


while True:
    get_and_send_urgent_messages()
    time.sleep(60)