import time
import datetime

import model
import fetchers

INTERVAL = datetime.timedelta(minutes=3)
HISTORYLEN = 25

def main():
    model.paladar_db.connect()
    regular_feed = model.ChannelType.get(name="regular")
    feedzilla_feed = model.ChannelType.get(name="feedzilla")
    model.paladar_db.close()
    try:
        while True:
            model.paladar_db.connect()
            channels = model.Channel.select()
            model.paladar_db.close()
            if channels.count() == 0:
                continue
            step = INTERVAL / channels.count()
            for channel in channels:
                print("Fetching {0}.".format(channel.title))
                if channel.type_ == regular_feed:
                    fetcher = fetchers.Regular(channel.url)
                elif channel.type_ == feedzilla_feed:
                    fetcher = fetchers.Feedzilla(channel.url)
                else:
                    # Unknown channel type. Ignore.
                    continue
                entries = fetcher.fetch_entries()
                entries.sort(key=lambda e: e['datetime'], reverse=True)
                for entry in entries:
                    try:
                        model.paladar_db.connect()
                        model.Entry.create(
                          url = entry['url'],
                          channel = channel,
                          pubtime = entry['datetime'],
                          title = entry['title'],
                          summary = entry['summary']
                        )
                        model.paladar_db.close()
                        print("Retrieved {0}.".format(entry['title']))
                    except model.IntegrityError:
                        break
                time.sleep(step.total_seconds())
    except KeyboardInterrupt:
        print("Stoping bot.")
    finally:
        model.paladar_db.close()

if __name__ == "__main__":
    main()
