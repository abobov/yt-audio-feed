import argparse
import multiprocessing
import urllib.request
from xml.etree import ElementTree as ET

FEED_SIZE = 40
NS_ATOM = 'http://www.w3.org/2005/Atom'


def extract_published(e): return e.find('{' + NS_ATOM + '}published').text


def get_feeds_from_opml(opml_file):
    opml = ET.parse(opml_file)
    items = opml.iter('outline')
    for item in items:
        if item.get('type') == 'rss':
            yield item.get('xmlUrl')


def extract_entries_from_feed(url):
    response = urllib.request.urlopen(url).read()
    return ET.fromstring(response).findall('{' + NS_ATOM + '}entry')


def get_entries(opml_file):
    pool = multiprocessing.Pool()
    feeds = pool.map(extract_entries_from_feed, get_feeds_from_opml(opml_file))
    entries = [item for sublist in feeds for item in sublist]
    return sorted(entries, key=extract_published, reverse=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('opml_file')
    args = parser.parse_args()

    ET.register_namespace('', NS_ATOM)
    ET.register_namespace('yt', 'http://www.youtube.com/xml/schemas/2015')
    ET.register_namespace('media', 'http://search.yahoo.com/mrss/')

    root = ET.Element('feed')
    title = ET.SubElement(root, 'title')
    title.text = 'YouTube subscriptions'
    entries = get_entries(args.opml_file)

    for entry in entries[:min(FEED_SIZE, len(entries))]:
        root.append(entry)

    ET.dump(root)


if __name__ == '__main__':
    main()
