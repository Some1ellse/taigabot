"""
A Discord bot that integrates with Taiga webhooks and REST API
to relay project updates to a Discord Forum channel.
This module handles webhook processing, API calls
message formatting, and Discord communication.
"""
import threading
import hmac
import hashlib
import asyncio
import discord
import requests # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from discord import (
    Intents,
    Client
)
from flask import Flask, request, abort
from waitress import serve
from handlers.data_handler import ( # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
    process_webhook,
    forum_tags
)
from handlers.taiga_api_auth import taiga_auth # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from config.config import(  # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
    DISCORD_TOKEN as TOKEN,
    FORUM_ID,
    SECRET_KEY,
    WEBHOOK_ROUTE)

# Create a Flask app
app = Flask(__name__)

def initialize_taiga_api():
    """Initialize the Taiga API"""
    print("Initializing Taiga API...")
    try:
        api_token = taiga_auth.get_token()
        if api_token:
            print("Taiga API initialized!")
        else:
            print("Failed to obtain authentication token!")
            print("Ensure TAIGA_USERNAME and TAIGA_PASSWORD are set in the environment variables")
    except (requests.RequestException, ValueError, KeyError) as e:
        # Handle specific exceptions as e:
        print(f"Error during authentication test: {e}")


# Bot setup
intents: Intents = Intents.default()
intents.members = True
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
        thread, embed, embed2, flags = process_webhook(payload)
        if isinstance(flags, dict) and 'is_test' in flags and flags['is_test']:
            print("Test Webhook - Ignoring")
            return '', 200
        if isinstance(flags, dict) and 'delete' in flags and flags['delete']:
            client.loop.create_task(delete_post(flags['user_story']))
            return '', 200
        if isinstance(flags, dict) and 'error' in flags and flags['error']:
            print(f"Webhook - Error {flags['error']}")
            return '', 500
        post_args = {
            'user_story': flags['user_story'], # pylint: disable=invalid-sequence-index
            'embed': embed,
            'embed2': embed2,
            'new_thread': thread,
            'description_new': flags['description_new'], # pylint: disable=invalid-sequence-index
            'mention': flags['mention']
            }

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
async def delete_post(user_story):
    """Try to delete a post from the indicated forum via bot"""
    print('Attempting to delete Forum Post...')
    channel = client.get_channel(FORUM_ID)
    if isinstance(channel, discord.ForumChannel):
        for thread in channel.threads:
            if thread.name.lower() == user_story.lower():
                await thread.delete()
                print('Forum Post deleted in Discord...')
                return

async def send_post(user_story, embed, embed2, new_thread=None, description_new=None, mention=None):
    """Try to send provided message to the indicated forum via bot"""
    is_thread = False
    if len(mention) == 1 and mention[0] == None:
        print('No mentions found')
    else:
        mention = await build_mentions(mention)
    try:
        print('Sending Forum Post to Discord...')
        channel = client.get_channel(FORUM_ID)
        # Get the applied tags from the new_thread if they exist
        tag_ids = new_thread.get('applied_tags', [])
        # Convert tag IDs to actual forum tag objects
        applied_tags = [tag for tag in channel.available_tags if tag.id in tag_ids]
        if isinstance(channel, discord.ForumChannel):
            for thread in channel.threads:
                if thread.name.lower() == user_story.lower():
                    print('Attempting to update Forum Post...')
                    await thread.edit(applied_tags=applied_tags)
                    if description_new is not None:
                        async for message in thread.history(limit=1, oldest_first=True):
                            await message.edit(content=new_thread['content'], suppress=True)
                    try:
                        messages = [message async for message in
                        thread.history(limit=3, oldest_first=True)]
                        if len(messages) >= 3:
                            #first_message = messages[0]
                            #print(f"Message type: {first_message.type}, Author: "
                            #f"{first_message.author}, System: {first_message.is_system()}")
                            await messages[2].edit(embed=embed2)
                            await messages[2].pin()
                            await thread.send(f'{mention}', embed=embed)
                        else:
                            await thread.send(embed=embed2)
                            await asyncio.sleep(5)
                            await thread.send(embed=embed)
                    except discord.Forbidden as e:
                        print(f"Forbidden error: {e}")
                        #print(f"Message details: ID={first_message.id}, Type={first_message.type}")
                    print('Forum Post updated in Discord...')
                    is_thread = True
                    return
            if not is_thread:
                print('Creating new Forum Post...')
                print(applied_tags)
                print(type(applied_tags))
                thread_with_message = await channel.create_thread(
                    name=new_thread['name'],
                    content=new_thread['content'],
                    auto_archive_duration=new_thread['auto_archive_duration'],
                    applied_tags=applied_tags,
                    suppress_embeds=True
                )

                try:
                    await thread_with_message.message.pin()
                    print('Forum Post created and pinned in Discord...')
                except discord.Forbidden:
                    print('Forum Post created in Discord...'
                          '(Could not pin message - Missing Manage Messages permission)')

                status_embed = await thread_with_message.thread.send(embed=embed2)
                print('Post status embed in new thread.')

                try:
                    await status_embed.pin()
                    print('Status embed posted and pinned in Discord...')
                except discord.Forbidden:
                    print('Status embed created in Discord...'
                          '(Could not pin message - Missing Manage Messages permission)')

                # Post the change embed in the new thread
                if embed:
                    await asyncio.sleep(5)
                    await thread_with_message.thread.send(embed=embed)
                    print('Change embed posted in new thread...')
        else:
            print('Forum Channel not found...')
    except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
        print(f'Discord API error: {e}')

async def build_mentions(mentions):
    """Builds a list of mentions from a list of user IDs"""
    channel = await client.fetch_channel(FORUM_ID)
    print('Building mentions...')
    mention_string = ''
    for user_id in mentions:
        user = next(
            (member for member in channel.guild.members
            if member.name.lower() == user_id.lower()), None
            )
        if not user:
            print(f"User {user_id} not found for mention.")
            continue
        mention_string += f'{user.mention}'
    return mention_string

async def get_members(forum_id: int):
    """Fetches all members of a guild and stores them in a list."""
    channel = await client.fetch_channel(forum_id)
    members = []
    async for member in channel.guild.fetch_members():
        members.append(member)
    print("Members fetched:", [member.name for member in members])
    return

async def get_forum_tags(forum_id: int):
    """Fetches available forum tags and stores them in a dataclass with a dictionary."""
    forum = await client.fetch_channel(forum_id)  # Fetch the forum channel

    if not isinstance(forum, discord.ForumChannel):
        print("This is not a forum channel!")
        return

    # Create a dictionary {tag_name: tag_id}
    tags_dict = {tag.name: tag.id for tag in forum.available_tags}

    # Store in the dataclass forum_tags
    forum_tags.tags = tags_dict
    #print("Forum tags updated:", forum_tags.tags)


async def update_forum_tags_periodically():
    """Updates forum tags every 5 minutes"""
    while True:
        await get_forum_tags(FORUM_ID)
        await asyncio.sleep(300)  # Sleep for 5 minutes (300 seconds)


# HANDLING THE STARTUP FOR BOT
@client.event
async def on_ready() -> None:
    """Print verification to console that bot is running"""
    print(f'{client.user} is now running')
    # Initial tags fetch
    await get_forum_tags(FORUM_ID)
    # Start periodic updates
    client.loop.create_task(update_forum_tags_periodically())
    #client.loop.create_task(get_members(FORUM_ID))


# MAIN ENTRY POINT
def main() -> None:
    """Kick everything off"""
    print('running client')
    client.run(token=TOKEN)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    initialize_taiga_api()
    main()
