# TODO: Set HTTP agents.

import datetime
import urllib.request
import json

import feedparser

class Feedzilla:
    _months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self, url=None):
        if url is None:
            url = "http://api.feedzilla.com/v1/"
            url += "articles.json?culture_code=pt-BR_br"
        self.url = url

    def _parse_datetime(self, dt):
        weekday, day, month, year, hms, offset = dt.split()
        hour, minute, second = hms.split(':')
        year = int(year)
        month = self._months.index(month) + 1
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        return datetime.datetime(year, month, day, hour, minute, second)

    def fetch_entries(self):
        stream = urllib.request.urlopen(self.url)
        obj = json.loads(stream.read().decode("utf8"))
        stream.close()
        articles = obj["articles"]
        entries = []
        for article in articles:
            entry = {}
            entry['datetime'] = self._parse_datetime(article['publish_date'])
            entry['url'] = article['url']
            entry['title'] = article['title']
            entry['summary'] = article['summary']
            entries.append(entry)
        entries.sort(key=lambda e: e['datetime'])
        return entries

    def fetch_info(self):
        info = {
          "url": self.url,
          "title": "Feedzilla news",
          "subtitle": "News from multiple sources agregated by Feedzilla."
        }
        return info

class Regular:

    def __init__(self, url):
        self.url = url

    def fetch_entries(self):
        d = feedparser.parse(self.url)
        entries = []
        for item in d.entries:
            entry = {}
            for prefix in "updated published created expired".split():
                if prefix in item:
                    key = prefix + "_parsed"
                    entry['datetime'] = datetime.datetime(*item[key][:6])
                    break
            entry['url'] = item.link
            entry['title'] = item.title
            entry['summary'] = item.summary
            entries.append(entry)
        entries.sort(key=lambda e: e['datetime'])
        return entries

    def fetch_info(self):
        d = feedparser.parse(self.url)
        info = {
          "url": d.feed.get("link", self.url),
          "title": d.feed.get("title", "Regular feed"),
          "subtitle": d.feed.get("subtitle", "Regular feed.")
        }
        return info
