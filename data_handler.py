import discord
import datetime
from taiga_api import get_user_story_history
from config import TAIGA_AUTH_TOKEN , TAIGA_BASE_URL

def process_webhook(data):
    """Process webhook data into strings to send to bot"""
    parsed_data = []
    print("Processing Started")
    print(data)
    change = data.get('change', {})
    diff = change.get('diff', {})
    tags = diff.get('tags', {})

    if data['type'] != 'userstory' and data['type'] != 'task' and data['type'] != 'issue':
        return
    print("Type checked")

    author = data['by']['full_name']
    author_url = data['by']['permalink']
    if data['by']['photo'] != None:
        author_icon_url = data['by']['photo']
    else:
        author_icon_url = "https://pm.ks-webserver.com/v-1721729942015/images/user-avatars/user-avatar-01.png"
    description = ''
    embed_title = None
    embed_description = None
    embed_field1_name = None
    embed_field2_name = None
    embed_field1_value = None
    embed_field2_value = None
    embed_field1_inline = None
    embed_field2_inline = None
    item_url = data['data']['permalink']
    new_description = None
    new_status = None
    old_status = None
    payload_action = data['action']
    payload_type = data['type']
    if data['data']['project']['logo_big_url'] != None:
        thumbnail_url = data['data']['project']['logo_big_url']
    else:
        thumbnail_url = "https://pm.ks-webserver.com/v-1721729942015/images/project-logos/project-logo-01.png"
    
    story_url = data['data']['permalink']
    ticket_number = story_url.split('/')[-1]
    user_story = '#' + ticket_number + ' ' + data['data']['subject']
    print("All variables set")

    
    if payload_action == 'create':
        color = discord.Color.green()
    elif payload_action == 'change':
        color = discord.Color.blue()
    elif payload_action == 'delete':
        color = discord.Color.red()
    print("Color set")


#    if isinstance(diff, dict) and 'kanban_order' in diff:
#        del diff['kanban_order']
#    if isinstance(tags, dict) and 'sprint_order' in tags:
#        del tags['sprint_order']
#
#    lines = [
#        f'A **{data['type']}** was **{data['action']}d** by [{data['by']['full_name']}](<{data['by']['permalink']}>) on {time}', # NOQA
#        f'- **__Project:__** [{data['data']['project']['name']}](<{data['data']['project']['permalink']}>)',
#    ]
    if payload_type == 'userstory':
        description = data['data']['description']
        if payload_action == 'change' and data['change']['comment']:
            if data['change']['comment'] is not None and data['change']['edit_comment_date'] is None and data['change']['delete_comment_date'] is None:
                embed_title = "A comment was created"
                embed_description = data['change']['comment']
                color = discord.Color.green()
            elif data['change']['comment'] is not None and data['change']['edit_comment_date'] is not None and data['change']['delete_comment_date'] is None:
                embed_title = "A comment was edited"
                embed_description = data['change']['comment']
                color = discord.Color.blue()
            elif data['change']['comment'] is not None and data['change']['edit_comment_date'] is None and data['change']['delete_comment_date'] is not None:
                embed_title = "A comment was deleted"
                embed_description = data['change']['comment']
                color = discord.Color.red()
        if payload_action == 'change' and diff:
            if isinstance(diff, dict) and 'description_diff' in diff:
                if diff['description_diff'] == 'Check the history API for the exact diff':
                    history = get_user_story_history(user_story_id=data['data']['id'], target_time=data['date'], time_threshold_ms=500)
                    if history is not None:
                        api_diff = history.get('diff', {})
                        if isinstance(api_diff, dict) and 'description' in api_diff:
                            embed_title = "The description was updated"
                            embed_description = "Check the pinned post for the new description"
                            new_description = api_diff['description'][1]
            elif isinstance(diff, dict) and 'status' in diff:
                print("Status change detected")
                embed_title = "The status was changed"
                embed_field1_name = "From"
                embed_field2_name = "To"
                embed_field1_value = diff['status']['from']
                embed_field2_value = diff['status']['to']
                embed_field1_inline = True
                embed_field2_inline = True

#        if payload_action == 'change' and data['change']['diff']:
#            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    if payload_type == 'task':
        description = data['data']['description']
#        if payload_action == 'change' and data['change']['comment']:
#            lines.append(f"    - **__Comment:__** {data['change']['comment']}")
#        if payload_action == 'change' and data['change']['diff']:
#            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    if payload_type == 'issue':
        description = data['data']['description']
#        if payload_action == 'change' and data['change']['comment']:
#            lines.append(f"    - **__Comment:__** {data['change']['comment']}")
#        if payload_action == 'change' and data['change']['diff']:
#            lines.append(f"    - **__Change:__** {data['change']['diff']}")

    description = f"# [#{ticket_number}]({story_url}) Description\n{description if description is not None else ''}"

    parsed_data = {
        "action": payload_action,
        "author": author,
        "author_url": author_url,
        "author_icon_url": author_icon_url,
        "color": color,
        "description": adjust_markdown(description),
        "embed_field1_name": embed_field1_name,
        "embed_field2_name": embed_field2_name,
        "embed_field1_value": embed_field1_value,
        "embed_field2_value": embed_field2_value,
        "embed_field1_inline": embed_field1_inline,
        "embed_field2_inline": embed_field2_inline,
        "embed_title": embed_title,
        "embed_description": embed_description,
        "new_description": new_description,
        "new_status": new_status,
        "old_status": old_status,
        "payload_type": payload_type,
        "user_story": user_story,
        "item_url": item_url,
        "thumbnail_url": thumbnail_url
    }
    print("Data has been processed")
    return parsed_data

def embed_builder(data):
    """Build an embed for the provided data"""
    embed = None
    embed = discord.Embed(
        title=data['embed_title'],
        description=data['embed_description'],
        url=data['item_url'],
        color=data['color'],
        timestamp=datetime.datetime.now(datetime.UTC),
    )
    embed.set_author(name=data['author'], url=data['author_url'], icon_url=data['author_icon_url'])
    embed.set_thumbnail(url=data['thumbnail_url'])
    if data['embed_field1_name']:
        embed.add_field(name=data['embed_field1_name'], value=data['embed_field1_value'], inline=data['embed_field1_inline'])
    if data['embed_field2_name']:
        embed.add_field(name=data['embed_field2_name'], value=data['embed_field2_value'], inline=data['embed_field2_inline'])
    embed.set_footer(text=data['user_story'], icon_url="https://taiga.io/media/images/Logo-text.width-140.png")
    return embed

def thread_builder(data):
    thread = {
        "name": data['user_story'],
        "content": data['description'],
        "auto_archive_duration": 4320
    }
    return thread

def truncate_string(s, max_chars=150):
    """Truncate strings to a max character limit or a line break, whichever comes first"""
    if len(s) > max_chars:
        s = s[:max_chars] + "..."
    if "\n" in s:
        s = s.split("\n")[0] + "..."
    return s


def adjust_markdown(content):
    """Adjust markdown to make it look good"""
    content = content.replace('####', '###')
    return content