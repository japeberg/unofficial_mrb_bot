# data_fetcher.py

from interface import implements, Interface
from unofficial_mrb_bot.mrb_message import MRBMessage
import requests
from lxml import html
from datetime import datetime


class IDataFetcher(Interface):
    def get_messages(self, line_id, line_name, url):
        """Get Messages from the url.
        Returns list of MRBMessage
        """


class DataFetcher(implements(IDataFetcher)):
    def __init__(self):
        self.line_id = None
        self.line_name = None
        self.url = None
        self.list_of_messages = list()

    def get_html_content(self):
        line_site = requests.get(url=self.url)
        site_content = line_site.content.decode("utf-8")
        return site_content

    def get_urgent_messages_as_xml(self):
        tree = html.fromstring(self.get_html_content())
        urgent_messages = tree.xpath('//div[@class="urgent-reports__text"]')
        return urgent_messages

    def get_messages(self, line_id, line_name, url):
        self.line_id = line_id
        self.line_name = line_name
        self.url = url
        urgent_messages_as_xml = self.get_urgent_messages_as_xml()
        for idx in range(0, len(urgent_messages_as_xml)):
            message = urgent_messages_as_xml[idx].xpath('p/text()')
            title = str(message[0])
            message = str(message[1])
            try:
                reason = str(message[2])
            except IndexError:
                reason = ""
            try:
                alternatives = str(message[3])
            except IndexError:
                alternatives = ""
            self.list_of_messages.append(MRBMessage(title=title,
                                                    message=message,
                                                    reason=reason,
                                                    alternatives=alternatives,
                                                    timestamp=datetime.now(),
                                                    line_id=self.line_id))
        return self.list_of_messages

a = DataFetcher().get_messages(url="https://www.mitteldeutsche-regiobahn.de/de/strecken/linienuebersicht-fahrplaene/linie/re-6-leipzig-chemnitz", line_id=123, line_name="RE 6")