# parser.py
from lxml import html
import requests
from datetime import datetime


# test parser
urls_to_parse = {
    'RE 6': 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-6-leipzig-chemnitz',
    'RE 3': 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-3-dresden-hof',
    'RB 30': 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-30-dresden-zwickau',
    'RB 45': 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-45-chemnitz-elsterwerda',
    'RB 110': 'https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/rb-110-leipzig-hbf-doebeln-hbf'
}



# return urgent messages as list of dict
def get_urgent_messages(url):

    messages = list()

    line_site = requests.get(url=url)
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
        split_message = {
            'title': title,
            'text': text,
            'reason': reason,
            'alternatives': alternatives,
            'sent': False,
            'read': datetime.now()
        }
        messages.append(split_message)
    return messages

# print(get_urgent_messages(urls_to_parse['RE 3']))