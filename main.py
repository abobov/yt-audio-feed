import argparse
import mimetypes
import multiprocessing
import signal
import sys
import urllib.request
from xml.etree import ElementTree as ET

import pafy
import pypandoc

DEFAULT_LIMIT = 40
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


def get_mime_type_by_extension(extension):
    key = '.' + extension
    if key in mimetypes.types_map:
        return mimetypes.types_map[key]
    return 'audio'


def summary_to_html(entry):
    text = list(entry.iter('{' + NS_MEDIA + '}description'))[0].text
    return pypandoc.convert_text(text, to='html', format='t2t')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('opml_file', help='OPML file from YouTube', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', help='Where to print XML output (default: stdout)',
                        default=sys.stdout.buffer, type=argparse.FileType('wb'))
    parser.add_argument('-n', '--limit', help=f'How many last videos to output (default: {DEFAULT_LIMIT})',
                        type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()

    ET.register_namespace('', NS_ATOM)
    ET.register_namespace('yt', 'http://www.youtube.com/xml/schemas/2015')
    ET.register_namespace('media', 'http://search.yahoo.com/mrss/')

    root = ET.Element('feed')
    title = ET.SubElement(root, 'title')
    title.text = 'YouTube subscriptions'
    entries = get_entries(args.opml_file)

    for entry in entries[:min(args.limit, len(entries))]:
        summary = ET.SubElement(entry, '{' + NS_ATOM + '}summary')
        summary.text = summary_to_html(entry)
        yt_link = entry.find('{' + NS_ATOM + '}link').attrib['href']
        try:
            best_audio = pafy.new(yt_link).getbestaudio()
        except IOError as e:
            continue
        if best_audio is not None:
            content = list(entry.iter('{http://search.yahoo.com/mrss/}content'))[0]
            content.attrib['url'] = best_audio.url
            content.attrib['type'] = get_mime_type_by_extension(best_audio.extension)
            root.append(entry)
    ET.ElementTree(root).write(args.output, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
