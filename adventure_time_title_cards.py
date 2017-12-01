"""
A short script to download the title cards from the imgur album at https://imgur.com/a/oPhjP
https://www.reddit.com/r/adventuretime/comments/2dsdnt/adventure_time_title_cards_wallpapers_1920x1080/

-ahvigil, November 2017
"""
import json
from urllib import urlretrieve as fetch
from multiprocessing import Pool
import requests
import os

import click

from HTMLParser import HTMLParser
h = HTMLParser()

imgur_client_id = ''
imgur_client_secret = ''

def retrieve(titlecard):
    # title = h.unescape(titlecard['title'])
    title = titlecard['title'] or titlecard['id']
    if not os.path.exists('%s.jpg' % title):
        fetch(titlecard['link'], '%s.jpg' % title)
        print title

@click.command()
@click.option('--fetch', is_flag=True)
def cli(fetch):
    if fetch:
        title_cards = requests.get('https://api.imgur.com/3/album/oPhjP/images',
                         headers={'Authorization': 'Client-ID %s' % imgur_client_id}).json()['data']
        with open('titlecards.json', 'w') as f:
            json.dump(title_cards, f)
    else:
        title_cards = json.load(open('titlecards.json'))

    print 'Fetching', len(title_cards), 'images'
    p = Pool(16)
    p.map(retrieve, title_cards)
    p.close()
    p.join()

if __name__ == '__main__':
    cli()
