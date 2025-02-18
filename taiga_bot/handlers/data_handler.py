"""
Data handler for Taiga webhooks
"""
import datetime
import re
from dataclasses import dataclass, field # pylint: disable=unused-import
from pprint import pprint
import discord
from .taiga_api import get_user_story_history, get_user_story, get_swimlane, get_user

@dataclass
class ForumTags:
    """Stores forum tags as a dictionary {tag_name: tag_id}."""
    tags: dict

#Singleton instance for global use
forum_tags = ForumTags(tags={})

class UserInfo:
    """Stores user information as a dictionary {user_id: user_name}."""
    def __init__(self, name=None, url=None, avatar=None, id=None):
        self.name = name
        self.url = url
        self.avatar = avatar
        self.id = id

    def get(self, dictionary):
        """Get user information from a dictionary"""
        self.name = safe_get(dictionary, ['by','full_name'])
        self.url = safe_get(dictionary, ['by', 'permalink'])
        self.avatar = safe_get(
            dictionary,
            ['by', 'photo']
        ) if safe_get(dictionary, ['by', 'photo']) else (
            "https://pm.ks-webserver.com/v-1721729942015/images/"
            "user-avatars/user-avatar-01.png"
        )
        self.id = safe_get(dictionary, ['by', 'id'])
        return self

userinfo = UserInfo()

def safe_get(dictionary, keys, default=None):
    """
    Safely extracts a value from a nested dictionary.

    :param dictionary: The dictionary to extract from.
    :param keys: A list or tuple of keys representing the nested path.
    :param default: The default value to return if any key is missing or empty.
    :return: The value found at the nested key path, or the default value.
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
            if current in (None, '', [], {}, ()):  # Handle empty values
                return default
        else:
            return default
    return current

# Example usage:
data = {
    'user': {
        'profile': {
            'name': 'Alice',
            'age': None,
            'address': {'city': 'New York'}
        }
    }
}

def process_webhook(payload):
    """Process webhook data into strings to send to bot"""
    is_test = False

    print("\n\nProcessing Started on...")
    pprint(payload)

    is_test = safe_get(payload, ['data', 'test'], False)
    if is_test:
        return None, None, None, {'is_test': is_test}

    print("\n\nDeterminting payload type...")

    payload_type = safe_get(payload, ['type'])
    if not payload_type:
        print("Malformed Webhook - Type not found")
        return None, None, None, {'error': 'Malformed Webhook - Type not found'}
    if payload_type == 'userstory':
        return userstory_handler(payload)
    if payload_type == 'task':
        return task_handler(payload)
    return None, None, None, {'error': 'invalid_payload'}

def task_handler(payload):
    """Handle a task webhook"""
    print("\n\nTask Webhook Received, Processing...")
    is_test = True

    if isinstance(payload, dict) and 'action' in payload:
        action = payload['action']
        if not action:
            print("Malformed Webhook - Action not found")
            return None

    if action == 'create':
        print("\n\nTask Webhook - Create, Processing...")



    return None, None, None, {'is_test': is_test}

def userstory_handler(payload):
    """Handle a user story webhook"""
    print("\n\nUserstory Webhook Received, Processing...")
    user = userinfo.get(payload)  # Store the returned user info
    action = safe_get(payload, ['action'])
    if not action:
        print("Malformed Webhook - Action not found")
        return None, None, None, {'error': 'Malformed Webhook - Action not found'}
    # Define variables
    # TODO: Update description emoji to match status' like closed or blocked.
    # TODO: Look into mentioning users who are tagged in comments.
    action_diff = []
    api_data = None
    assigned = safe_get(payload, ['data', 'assigned_to'])
    assigned_users = safe_get(payload, ['data', 'assigned_users'])
    blocked = safe_get(payload, ['data', 'is_blocked']) # pylint: disable=unused-variable
    blocked_reason = safe_get(
        payload,
        ['data', 'blocked_note']
        ) if safe_get(payload, ['data', 'blocked_note']) else "No reason provided"
    description = safe_get(payload, ['data', 'description'])
    description_new = None
    due_date = safe_get(payload, ['data', 'due_date'])
    due_date_old = None
    due_date_reason = safe_get(payload, ['data', 'due_date_reason'])
    embed = None
    embed2 = None
    embed_color = None
    has_team_requirement = safe_get(payload, ['data', 'has_team_requirement'])
    has_client_requirement = safe_get(payload, ['data', 'has_client_requirement'])
    history = None
    link = safe_get(payload, ['data', 'permalink'])
    mention = []
    milestone = safe_get(payload, ['data', 'milestone', 'name'])
    owner = safe_get(payload, ['data', 'owner', 'full_name'])
    owner_url = safe_get(payload, ['data', 'owner', 'permalink'])
    owner_icon_url = safe_get(
            payload,
            ['data', 'owner', 'photo']
        ) if safe_get(payload, ['data', 'owner', 'photo']) else (
            "https://pm.ks-webserver.com/v-1721729942015"
            "/images/user-avatars/user-avatar-01.png"
        )
    status = safe_get(payload, ['data', 'status', 'name'])
    story_id = safe_get(payload, ['data', 'id'])
    swimlane = safe_get(payload, ['data', 'swimlane'])
    swimlane_id = safe_get(payload, ['data', 'swimlane_id'])
    tags = safe_get(payload, ['data', 'tags'])
    thread = None
    ticket_number = safe_get(payload, ['data', 'ref'])
    title = safe_get(payload, ['data', 'subject'])
    title_plain = f"#{ticket_number} {title}"
    to_from = {}
    thumbnail_url = safe_get(
            payload,
            ['data', 'project', 'logo_big_url']
        ) if safe_get(payload, ['data', 'project', 'logo_big_url']) else (
            "https://pm.ks-webserver.com/v-1721729942015"
            "/images/project-logos/project-logo-01.png"
        )
    watchers = safe_get(payload, ['data', 'watchers'])


    # Initial API call to catch pre-existing objects.
    if action != 'delete':
        api_data = get_user_story(story_id)
        swimlane_id = safe_get(api_data, ['swimlane'])
        if swimlane_id:
            api_data = get_swimlane(swimlane_id)
            swimlane = safe_get(api_data, ['name'])
        api_data = None

    if action == 'create':
        action_diff.append("A new user story was created")
        embed_color = discord.Color.green()

    if action == 'change':
        change = safe_get(payload, ['change'])
        if safe_get(change, ['comment']) is not None:
            if (
                change['comment'] != '' and
                change['edit_comment_date'] is None and
                change['delete_comment_date'] is None
                ):
                action_diff.append("New Comment!")
                action_diff.append(change['comment'])
                embed_color = discord.Color.green()
            elif (
                change['comment'] is not None and
                change['edit_comment_date'] is not None and
                change['delete_comment_date'] is None
                ):
                action_diff.append("Comment edited.")
                action_diff.append(change['comment'])
                embed_color = discord.Color.blue()
            elif (
                change['comment'] is not None and
                change['delete_comment_date'] is not None
                ):
                action_diff.append("Comment Deleted!")
                action_diff.append(change['comment'])
                embed_color = discord.Color.red()
        diff = safe_get(change, ['diff'])
        if safe_get(diff, ['assigned_users', 'from']) is not None:
            action_diff.append(
                "The assigned users were changed."
                " Login to Tiaga to see the new assignements."
                )
            embed_color = discord.Color.blue()
        if safe_get(diff, ['is_blocked', 'from']) is not None:
            action_diff.append("The blocked status was updated")
            to_from['to'] = blocked
            embed_color = discord.Color.blue()
            if diff['is_blocked']['from']:
                to_from['from'] = "Yes"
            else:
                to_from['from'] = "No"
        if safe_get(diff, ['client_requirement', 'from']) is not None:
            action_diff.append("The client requirement was updated")
            to_from['to'] = has_client_requirement
            embed_color = discord.Color.blue()
            if diff['client_requirement']['from'] is True:
                to_from['from'] = "Yes"
            else:
                to_from['from'] = "None"
        if safe_get(diff, ['description_diff']) is not None:
            if diff['description_diff'] == 'Check the history API for the exact diff':
                history = get_user_story_history(user_story_id=data['data']['id'],
                    target_time=data['date'], time_threshold_ms=500)
                if history is not None:
                    api_diff = history.get('diff', {})
                    if safe_get(api_diff, ['description']) is not None:
                        action_diff.append("The description was updated. "
                        "Check pinned for new description!")
                    description = api_diff['description'][1]
                    embed_color = discord.Color.blue()
                else:
                    action_diff.append("Unknown Change was detected in the API")
                    print("Unknown change detected in the API")
        if safe_get(diff, ['due_date', 'to']) is not None:
            due_date = diff['due_date']['to']
            to_from['from'] = diff['due_date']['from']
            to_from['to'] = due_date
            action_diff.append("The due date was changed.")
        if safe_get(diff, ['swimlane', 'to']) is not None:
            swimlane = diff['swimlane']['to']
            action_diff.append("The swimlane was updated")
        if safe_get(diff, ['status', 'from']) is not None:
            action_diff.append("The status was updated")
            to_from['to'] = status
            to_from['from'] = diff['status']['from']
            embed_color = discord.Color.blue()
        if safe_get(diff, ['team_requirement', 'from']) is not None:
            action_diff.append("The team requirement was updated")
            to_from['to'] = has_team_requirement
            if diff['team_requirement']['from'] is True:
                to_from['from'] = "Yes"
            else:
                to_from['from'] = "None"
            embed_color = discord.Color.blue()

    if (action in ['create', 'change']):
        if assigned_users is None:
            assigned_users = []
        if watchers is None:
            watchers = []
        mention_users = assigned_users + [item for item in watchers if item not in assigned_users]
        mention = []
        for user in mention_users:
            api_data = None
            api_data = get_user(user)
            if isinstance(api_data, dict) and 'bio' in api_data:
                mention.append(find_mention(api_data['bio']))
                print(mention)
        full_description = adjust_markdown(description)

        if len(full_description) > 2000:
            description = full_description[:1100]
            description = (":inbox_tray:\n\n" + description +
            "\n\n### Description Truncated. Log into Taiga to see full description."
            )
        else:
            description = ":inbox_tray:\n\n" + full_description

        if swimlane:
            swimlane_id = forum_tags.tags[swimlane]
        else:
            swimlane_id = None
        if action_diff[0] == "The description was updated. Check pinned for new description!":
            description_new = True
        if not description:
            description = "No description provided."
        if swimlane_id:
            thread = {
            "name": title_plain,
            "content": description,
            "applied_tags": [swimlane_id],
            "auto_archive_duration": 4320
            }
        else:
            thread = {
            "name": title_plain,
            "content": description,
            "auto_archive_duration": 4320
            }

    flags = {}
    flags['user_story'] = title_plain
    if description_new:
        flags['description_new'] = description_new
    else:
        flags['description_new'] = None
    if swimlane_id:
        flags['swimlane'] = swimlane_id
    else:
        flags['swimlane'] = None
    if action == 'delete':
        flags['delete'] = True
    if mention:
        flags['mention'] = mention

    if action == 'change':
        embed = discord.Embed(
            title=title_plain,
            description='',
            url=link,
            color=embed_color,
            timestamp=datetime.datetime.now(datetime.UTC),
        )
        embed.add_field(
            name=action_diff[0],
            value='-',
            inline=False
            )
        if len(action_diff) > 1:
            embed.add_field(
                name='',
                value=action_diff[1],
                inline=False
                )
#            embed.add_field(
#                name='',
#                value=action_diff[1],
#                inline=False
#                )
        embed.set_author(
            name=userinfo.name,
            url=userinfo.url,
            icon_url=userinfo.avatar
            )
        embed.set_thumbnail(url=thumbnail_url)
        if to_from:
            embed.add_field(
                name="From",
                value=to_from['from'],
                inline=True
                )
            embed.add_field(
                name="To",
                value=to_from['to'],
                inline=True
                )
        embed.set_footer(
            text='Powered by Taiga REST API | Coded by @Some1ellse',
            icon_url="https://taiga.io/media/images/Logo-text.width-140.png"
            )

    embed2 = discord.Embed(
        title=title_plain,
        description='Current Status (Always Updated)',
        url=link,
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now(datetime.UTC),
    )
    embed2.set_author(
        name=owner,
        url=owner_url,
        icon_url=owner_icon_url
        )
    embed2.set_thumbnail(url=thumbnail_url)
    embed2.add_field(
        name="Status",
        value=status,
        inline=True
        )
    embed2.add_field(
        name="Assigned to",
        value=assigned,
        inline=True
        )
    embed2.add_field(
        name="Due Date",
        value=due_date,
        inline=True
        )
    embed2.add_field(
        name='',
        value='-',
        inline=False
        )
    embed2.add_field(
        name='Blocked',
        value=blocked_reason,
        inline=True
        )
    embed2.add_field(
        name='Team Req.',
        value=has_team_requirement,
        inline=True
        )
    embed2.add_field(
        name='Client Req.',
        value=has_client_requirement,
        inline=True
        )
    embed2.set_footer(
        text='Powered by Taiga REST API | Coded by @Some1ellse',
        icon_url="https://taiga.io/media/images/Logo-text.width-140.png"
        )

    return thread, embed, embed2, flags

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
    embed.set_author(
        name=data['author'],
        url=data['author_url'],
        icon_url=data['author_icon_url']
        )
    embed.set_thumbnail(url=data['thumbnail_url'])
    if data['embed_field1_name']:
        embed.add_field(
            name=data['embed_field1_name'],
            value=data['embed_field1_value'],
            inline=data['embed_field1_inline']
            )
    if data['embed_field2_name']:
        embed.add_field(
            name=data['embed_field2_name'],
            value=data['embed_field2_value'],
            inline=data['embed_field2_inline']
            )
    embed.set_footer(
        text='Powered by Taiga REST API | Coded by @Some1ellse',
        icon_url="https://taiga.io/media/images/Logo-text.width-140.png"
        )
    return embed

def split_content(content, limit=1900):
    """Split content into two parts if it exceeds Discord's limit
    
    Args:
        content (str): The content to split
        limit (int): Maximum length for the first part
        
    Returns:
        tuple: (first_part, second_part) where second_part is None if no split needed
    """
    if len(content) <= limit:
        return content, None

    # Try to split at a newline near the middle
    split_index = content.rfind('\n', 0, limit)
    if split_index == -1:
        # If no newline found, split at a space
        split_index = content.rfind(' ', 0, limit)
        if split_index == -1:
            # If no space found, just split at the limit
            split_index = limit

    return content[:split_index], content[split_index:].lstrip()

def thread_builder(data):
    """ Build a thread from the provided data """
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

def find_mention(text):
    """Find a mention in text"""
    match = re.search(r"@([^\s\r\n]+)", text)
    return match.group(1) if match else None
