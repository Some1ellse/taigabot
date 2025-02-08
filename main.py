"""
A Discord bot that integrates with Taiga webhooks to relay project updates to a Discord channel.
This module handles webhook processing, message formatting, and Discord communication.
"""

import datetime
import threading
import json
import hmac
import hashlib
import os
from typing import Final

# REMOVE BEFORE DEPLOY
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
# REMOVE ABOVE BEFORE DEPLOY

import discord
from discord import Intents, Client
from flask import Flask, request, abort
from waitress import serve
from date_time import resolve

TOKEN: Final[str] = os.environ['DISCORD_TOKEN']
CHANNEL_ID: Final[int] = int(os.environ['CHANNEL_ID'])
FORUM_ID: Final[int] = int(os.environ['FORUM_ID'])
SECRET_KEY: Final[str] = os.environ['SECRET_KEY']

# Create a Flask app
app = Flask(__name__)

# Bot setup
intents: Intents = Intents.default()
client: Client = Client(intents=intents)


# Webhook listener
@app.route('/webhook', methods=['POST'])
def respond():
    """Catch headers and payload, verify signature and pass payload along if verified"""
    headers = dict(request.headers)
    if 'X-Taiga-Webhook-Signature' not in headers:
        abort(401)
    signature = headers['X-Taiga-Webhook-Signature']
    payload = request.json
    data = json.dumps(payload)
    valid = verify_signature(SECRET_KEY, data) == signature
    if valid:
        process_webhook(payload)
        return '', 200
    else:
        abort(401)


def verify_signature(key, data):
    """Verify signature with key"""
    mac = hmac.new(key.encode("utf-8"), msg=data.encode("utf8"), digestmod=hashlib.sha1)
    return mac.hexdigest()


def truncate_string(s, max_chars=150):
    """Truncate strings to a max character limit or a line break, whichever comes first"""
    if len(s) > max_chars:
        s = s[:max_chars] + "..."
    if "\n" in s:
        s = s.split("\n")[0] + "..."
    return s


def process_webhook(data):
    """Process webhook data into strings to send to bot"""
    print(data)
    print(type(data))
    change = data.get('change', {})
    diff = change.get('diff', {})
    tags = diff.get('tags', {})
    time = str(data['date'])
    time = resolve(time)
    payload_type = data['type']
    if payload_type != 'userstory' and payload_type != 'task' and payload_type != 'issue':
        return
    payload_action = data['action']
    if isinstance(diff, dict) and 'description_diff' in diff:
        if diff['description_diff'] == 'Check the history API for the exact diff':
            del diff['description_diff']
    if isinstance(diff, dict) and 'kanban_order' in diff:
        del diff['kanban_order']
    if isinstance(tags, dict) and 'sprint_order' in tags:
        del tags['sprint_order']
#    if data.get('change', {}).get('diff', {}).get('kanban_order'):
#        del data['change']['diff']['kanban_order']
#    if data.get('change', {}).get('diff', {}).get('tags').get('sprint_order'):
#        del data['change']['diff']['tags']['sprint_order']
#    if data.get('change', {}).get('diff', {}).get('description_diff'):
#        if data['change']['diff']['description_diff'] == 'Check the history API for the exact diff':
#            del data['change']['diff']['description_diff']
    lines = [
        f'A **{data['type']}** was **{data['action']}d** by [{data['by']['full_name']}](<{data['by']['permalink']}>) on {time}', # NOQA
        f'- **__Project:__** [{data['data']['project']['name']}](<{data['data']['project']['permalink']}>)',
    ]
    if payload_type == 'userstory':
        lines.append(f'  - **__User Story:__** [{data['data']['subject']}](<{data['data']['permalink']}>)')
        user_story = data['data']['subject']
        print(user_story)
        lines.append(f'  - **__Status:__** {data['data']['status']['name']}')
        lines.append(f'  - **__Description:__** {data['data']['description']}')
        if payload_action == 'change' and data['change']['comment']:
            lines.append(f'    - **__Comment:__** {data['change']['comment']}')
        if payload_action == 'change' and data['change']['diff']:
            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    if payload_type == 'task':
        lines.append(f'- **__User Story:__** [{data['data']['user_story']['subject']}](<{data['data']['user_story']['permalink']}>)') # NOQA
        user_story = data['data']['user_story']['subject']
        print(user_story)
        lines.append(f'- **__Task:__** [{data['data']['subject']}](<{data['data']['permalink']}>)')
        lines.append(f'  - **__Status:__** {data['data']['status']['name']}')
        lines.append(f"  - **__Description:__** {data['data']['description']}")
        if payload_action == 'change' and data['change']['comment']:
            lines.append(f"    - **__Comment:__** {data['change']['comment']}")
        if payload_action == 'change' and data['change']['diff']:
            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    if payload_type == 'issue':
        lines.append(f'- **__Issue:__** [{data['data']['subject']}](<{data['data']['permalink']}>)')
        user_story = data['data']['subject']
        print(user_story)
        lines.append(f'  - **__Status:__** {data['data']['status']['name']}')
        lines.append(f"  - Description:__** {data['data']['description']}")
        if payload_action == 'change' and data['change']['comment']:
            lines.append(f"    - **__Comment:__** {data['change']['comment']}")
        if payload_action == 'change' and data['change']['diff']:
            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    truncated_lines = []
    for line in lines:
        truncated_line = truncate_string(line)
        truncated_lines.append(truncated_line)
    message = '\n'.join(truncated_lines)
    print(message)
    client.loop.create_task(send_message(message))
    project_url = data['data']['project']['permalink']
    print('project url is...', project_url)
    embed = discord.Embed(
        title=data['data']['project']['name'],
        description=payload_action,
        url=project_url,
        color=discord.Color.dark_teal(),
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.set_author(name="Kyrie Bot", url=project_url, icon_url="")
    client.loop.create_task(send_embed(embed))
    client.loop.create_task(send_post(user_story, message))


def run_flask():
    """Run the Flask app"""
    serve(app, host='0.0.0.0', port=5000)

async def send_post(user_story, message):
    """Try to send provided message to the indicated forum via bot"""
    try:
        print('Sending Forum Post to Discord...')
        channel = client.get_channel(FORUM_ID)
        await channel.create_thread(
            name=user_story,
            content=message,
            )
    except Exception as e:
        print(e)

async def send_embed(embed_message):
    """Try to send provided embed to the indicated channel via bot"""
    try:
        print('Sending Embed to Discord...')
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(embed=embed_message)
    except Exception as e:
        print(e)


# MESSAGE FUNCTIONALITY
async def send_message(bot_message):
    """Try to send provided message to the indicated channel via bot"""
    try:
        print('Sending Message to Discord...')
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(bot_message)
    except Exception as e:
        print(e)


# HANDLING THE STARTUP FOR BOT
@client.event
async def on_ready() -> None:
    """Print verification to console that bot is running"""
    print(f'{client.user} is now running')


# MAIN ENTRY POINT
def main() -> None:
    """Kick everything off"""
    print('running client')
    client.run(token=TOKEN)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    main()
