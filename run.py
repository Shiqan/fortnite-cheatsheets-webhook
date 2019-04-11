import logging
import os

import redis
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from dataclasses import dataclass


@dataclass
class CheatSheet:
    id: str
    title: str
    url: str
    permalink: str


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))

# Create webhook
webhook = DiscordWebhook(url=os.getenv('WEBHOOK_URL', ''))

# Redis cache
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)


def get_cache():
    redis_cache = conn.lrange('cache', 0, -1) or []
    log.debug(f"Number of items in cache: {len(redis_cache)}")
    return [i.decode() for i in redis_cache]


def add_to_cache(sheets):
    log.debug(f"Adding to cache {sheets}")
    conn.lpush('cache', *sheets)


def parse_cheat_sheets(feed):
    log.info('parsing feed...')
    sheets = []

    data = feed.get('data', [])
    if data:
        posts = (post for post in data.get(
            'children', []) if post.get('kind') == 't3')
        fortnite_posts = (post['data'] for post in posts if post.get(
            'data', {}).get('subreddit') == 'FortNiteBR')
        cheatsheets = [post for post in fortnite_posts if 'challanges' in post.get(
            'title', '').lower() or 'cheat sheet' in post.get('title', '').lower()]
        for sheet in cheatsheets:
            if sheet.get('id') not in get_cache():
                sheets.append(CheatSheet(id=sheet.get('id'), title=sheet.get('title'), url=sheet.get(
                    'url'), permalink=sheet.get('permalink')))

    if sheets:
        add_to_cache(sheet.id for sheet in sheets)
    return sheets


def fetch():
    user = os.getenv('REDDIT_USER', 'thesquatingdog')
    url = f'http://api.reddit.com/user/{user}/submitted/?sort=new'
    response = requests.get(
        url, headers={'User-agent': 'fortnite-cheatsheets-webhook 0.1'})
    return response.json()


def gather_posts():
    logging.info('gathering posts...')
    feed = fetch()
    sheets = parse_cheat_sheets(feed)
    for sheet in sheets:
        embed = DiscordEmbed(title=sheet.title)
        embed.set_image(url=sheet.url)
        webhook.add_embed(embed)
        webhook.execute()
        webhook.remove_embed(-1)


if __name__ == '__main__':
    gather_posts()
