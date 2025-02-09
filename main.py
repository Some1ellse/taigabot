"""
A Discord bot that integrates with Taiga webhooks to relay project updates to a Discord channel.
This module handles webhook processing, message formatting, and Discord communication.
"""
import threading
import hmac
import hashlib
import asyncio
import discord
from discord import Intents, Client
from flask import Flask, request, abort
from waitress import serve
from data_handler import process_webhook, embed_builder, thread_builder
from config import DISCORD_TOKEN as TOKEN, CHANNEL_ID, FORUM_ID, SECRET_KEY, WEBHOOK_ROUTE

# Create a Flask app
app = Flask(__name__)

# Bot setup
intents: Intents = Intents.default()
client: Client = Client(intents=intents)


# Webhook listener
@app.route(WEBHOOK_ROUTE or '/webhook', methods=['POST'])
def respond():
    """Catch headers and payload, verify signature and pass payload along if verified"""
    headers = dict(request.headers)
    if 'X-Taiga-Webhook-Signature' not in headers:
        print("Missing X-Taiga-Webhook-Signature header")
        abort(401)
    signature = headers['X-Taiga-Webhook-Signature']
    raw_data = request.get_data().decode('utf-8')
    valid = verify_signature(SECRET_KEY, raw_data) == signature
    payload = request.json
    if valid:
        print("Attempting to process webhook...")
        processed_data = process_webhook(payload)
        if processed_data == 'Test Webhook - Ignoring':
            return '', 200
        print("Attempting to build embed")
        embed = embed_builder(processed_data)
        print("Attempting to build thread")
        new_thread = thread_builder(processed_data)
        print("Attempting to send messages")
        # Only include new_description if it exists
        post_args = {
            'user_story': processed_data['user_story'],
            'embed': embed,
            'new_thread': new_thread
        }
        if processed_data['new_description'] is not None:
            post_args['new_description'] = processed_data['new_description']

        client.loop.create_task(send_post(**post_args))
        return '', 200
    else:
        print("Signature verification failed")
        abort(401)


def verify_signature(key, data):
    """Verify signature with key"""
    mac = hmac.new(key.encode("utf-8"), msg=data.encode("utf8"), digestmod=hashlib.sha1)
    return mac.hexdigest()


def run_flask():
    """Run the Flask app"""
    serve(app, host='0.0.0.0', port=5000)

# MESSAGE FUNCTIONALITY

async def send_post(user_story, embed, new_thread, new_description=None):
    """Try to send provided message to the indicated forum via bot"""
    is_thread = False
    try:
        print('Sending Forum Post to Discord...')
        channel = client.get_channel(FORUM_ID)
        if isinstance(channel, discord.ForumChannel):
            for thread in channel.threads:
                if thread.name.lower() == user_story.lower():
                    print('Attempting to update Forum Post...')
                    if new_description is not None:
                        async for message in thread.history(limit=1, oldest_first=True):
                            await message.edit(content=new_description)
                    await thread.send(embed=embed)
                    print('Forum Post updated in Discord...')
                    is_thread = True
                    return
            if not is_thread:
                print('Creating new Forum Post...')
                thread_with_message = await channel.create_thread(
                    name=new_thread['name'],
                    content=new_thread['content'],
                    auto_archive_duration=new_thread['auto_archive_duration'],
                    suppress_embeds=True
                )
                try:
                    await thread_with_message.message.pin()
                    print('Forum Post created and pinned in Discord...')
                except discord.Forbidden:
                    print('Forum Post created in Discord...'
      '(Could not pin message - Missing Manage Messages permission)')
                return
        else:
            print('Forum Channel not found...')
    except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
        print(f'Discord API error: {e}')



async def send_embed(embed_message):
    """Try to send provided embed to the indicated channel via bot"""
    try:
        print('Sending Embed to Discord...')
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(embed=embed_message)
    except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
        print(f'Discord API error: {e}')


async def send_message(bot_message):
    """Try to send provided message to the indicated channel via bot"""
    try:
        print('Sending Message to Discord...')
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(bot_message)
    except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
        print(f'Discord API error: {e}')


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
