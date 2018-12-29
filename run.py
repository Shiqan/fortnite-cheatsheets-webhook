import asyncio
import logging
import os
import redis

import aiohttp
from discord_webhook import DiscordEmbed, DiscordWebhook

from dataclasses import dataclass
from worker import conn


@dataclass
class CheatSheet:
    id: str
    title: str
    url: str
    permalink: str


# Create webhook
webhook = DiscordWebhook(url=os.getenv(
    'WEBHOOK_URL', 'https://discordapp.com/api/webhooks/528592348939157504/sY0Jc9MpBxsRKNUQVXxz31bV23nXmGdzLpNs4R84sjJXRTmsBqzjJidn23Rw4dXB_u52'))

# conn.delete('cache')
redis_cache = conn.lrange('cache', 0, -1) or []
cache = [i.decode() for i in redis_cache]

def add_to_cache(sheets):
    conn.lpush('cache', *sheets)

def parse_cheat_sheets(feed):
    logging.info('parsing feed...')
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
            if sheet.get('id') not in cache:
                sheets.append(CheatSheet(id=sheet.get('id'), title=sheet.get('title'), url=sheet.get(
                    'url'), permalink=sheet.get('permalink')))
    
    if sheets:
        add_to_cache(sheet.id for sheet in sheets)
    return sheets


async def fetch(session):
    user = os.getenv('REDDIT_USER', 'thesquatingdog')
    url = f'http://api.reddit.com/user/{user}/submitted/?sort=new'
    async with session.get(url) as response:
        return await response.json()


async def gather_posts():
    logging.info('gathering posts...')
    async with aiohttp.ClientSession() as session:
        feed = await fetch(session)
        sheets = parse_cheat_sheets(feed)
        for sheet in sheets:
            embed = DiscordEmbed(title=sheet.title)
            embed.set_image(url=sheet.url)
            webhook.add_embed(embed)
            webhook.execute()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gather_posts())
