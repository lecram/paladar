# TODO: Set HTTP agents.

import datetime
import urllib.request
import json

import feedparser

_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def _parse_datetime(dt):
    weekday, day, month, year, hms, offset = dt.split()
    hour, minute, second = hms.split(':')
    year = int(year)
    month = _months.index(month) + 1
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    return datetime.datetime(year, month, day, hour, minute, second)

def feedzilla(url=None):
    if url is None:
        url = "http://api.feedzilla.com/v1/"
        url += "articles.json?culture_code=pt-BR_br"
    stream = urllib.request.urlopen(url)
    obj = json.loads(stream.read().decode("utf8"))
    stream.close()
    articles = obj["articles"]
    entries = []
    for article in articles:
        entry = {}
        entry['datetime'] = _parse_datetime(article['publish_date'])
        entry['url'] = article['url']
        entry['title'] = article['title']
        entry['summary'] = article['summary']
        entries.append(entry)
    entries.sort(key=lambda e: e['datetime'])
    return entries

def regular(url):
    d = feedparser.parse(url)
    entries = []
    for item in d.entries:
        entry = {}
        entry['datetime'] = datetime.datetime(*item.published_parsed[:6])
        entry['url'] = item.link
        entry['title'] = item.title
        entry['summary'] = item.summary
        entries.append(entry)
    entries.sort(key=lambda e: e['datetime'])
    return entries
