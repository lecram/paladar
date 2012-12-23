import time
import datetime
import random

INTERVAL = datetime.timedelta(minutes=3)
HISTORYLEN = 25

class Channel:
    live = []

    def __init__(self, url, fetcher):
        self.fetcher = fetcher(url)
        secsint = INTERVAL.total_seconds()
        secs = random.random() * secsint
        self.remaining = datetime.timedelta(seconds=secs)
        self.info = self.fetcher.fetch_info()

    def fetch(self):
        return self.fetcher.fetch_entries()


# FeedBot's main goal is to continually retrieve new feed entries from a
#  list of channels.
# Secondary goals include:
#  * retrieve new entries as soon as possible;
#  * fetch feed servers as infrequently as possible;
#  * distribute fetch schedules as separated as possible.
class FeedBot:
    running = False
    channels = []

    def addchannel(self, url, fetcher):
        self.channels.append(Channel(url, fetcher))

    def run(self):
        self.running = True
        while self.running:
            self.channels.sort(key=lambda c: c.remaining)
            towait = self.channels[0].remaining
            time.sleep(towait.total_seconds())
            for channel in self.channels:
                if channel.remaining == towait:
                    if channel.live:
                        lasturl = channel.live[0]['url']
                    else:
                        lasturl = None
                    entries = channel.fetch()
                    entries.sort(key=lambda e: e['datetime'], reverse=True)
                    index = 0
                    for index, entry in enumerate(entries):
                        if entry['url'] == lasturl:
                            break
                    if index:
                        entries = entries[:index]
                        fmt = "{0} new entries in {1}."
                        print(fmt.format(index, channel.info['title']))
                        for i, entry in enumerate(entries):
                            print(i, entry['datetime'])
                        # birth(entries)
                        # death(self.live[-index:]
                        channel.live = entries + channel.live[:-index]
                    else:
                        fmt = "No new entries in {0}."
                        print(fmt.format(channel.info['title']))
                    channel.remaining = INTERVAL
                else:
                    channel.remaining -= towait

    def stop(self):
        self.running = False

if __name__ == "__main__":
    import fetchers
    bot = FeedBot()
    bot.addchannel(None, fetchers.Feedzilla)
    bot.addchannel("http://reddit.com/.rss", fetchers.Regular)
    for channel in bot.channels:
        print(channel.info['title'])
    bot.run()
