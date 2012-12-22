import time
import datetime

INITINTERVAL = datetime.timedelta(minutes=5)
HISTORYLEN = 25
PATIENCE = 1.5

class Channel:
    updates = 0
    remaining = datetime.timedelta(seconds=5)
    live = []

    # fetcher(url) -> entries
    # entry = {datetime, url, title, summary}
    def __init__(self, url, fetcher):
        self.url = url
        self.fetcher = fetcher
        self.interval = INITINTERVAL

    def fetch(self):
        return self.fetcher(self.url)


# FeedBot's main goal is to continually retrieve new feed entries from a
#  list of channels.
# Secondary goals include:
#  * retrieve new entries as soon as possible;
#  * fetch feed servers as infrequently as possible;
#  * distribute fetch schedules as separeted as possible.
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
                    for index, entry in enumerate(entries):
                        if entry['url'] == lasturl:
                            break
                    if index == 0:
                        sec = channel.interval.total_seconds()
                        sec *= PATIENCE
                        channel.interval = datetime.timedelta(seconds=sec)
                    else:
                        entries = entries[:index]
                        print("{0} new entries.".format(index))
                        for i, entry in enumerate(entries):
                            print(i, entry['url'])
                        # birth(entries)
                        # death(self.live[-index:]
                        channel.live = entries + channel.live[:-index]
                        if channel.updates:
                            sec = channel.interval.total_seconds()
                            sec = (channel.updates * sec + index) / (channel.updates + 1)
                            channel.interval = datetime.timedelta(seconds=sec)
                    channel.remaining = channel.interval
                    channel.updates += 1
                    print(channel.interval)
                else:
                    channel.remaining -= towait

    def stop(self):
        self.running = False

if __name__ == "__main__":
    import fetchers
    bot = FeedBot()
    bot.addchannel("http://reddit.com/.rss", fetchers.regular)
    bot.run()
