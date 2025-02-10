"""
Data handler for Taiga webhooks
"""
import datetime
import time
from dataclasses import dataclass, field # pylint: disable=unused-import
from pprint import pprint
import discord
from .taiga_api import get_user_story_history, get_user_story, get_swimlane

@dataclass
class ForumTags:
    """Stores forum tags as a dictionary {tag_name: tag_id}."""
    tags: dict

#Singleton instance for global use
forum_tags = ForumTags(tags={})

@dataclass
class Userstory:
    """Dataclass for user story data"""
    action: dict
    assigned: str
    blocked: dict #= field(default_factory=lambda: {"Is Blocked": None, "Reason": None})
    description: dict
    due_date: dict #= field(default_factory=lambda: {"Date": None, "Reason": None})
    has_client_requirement: bool
    has_team_requirement: bool
    link: str
    milestone: str
    status: dict #= field(default_factory=lambda: {"Current": None, "Old": None})
    story_id: int
    tags: dict #= field(default_factory=lambda: {"Swimlane": None, "Tags": []})
    title: dict #= field(default_factory=lambda: {"Plain": None, "Linked": None})


def process_webhook(data):
    """Process webhook data into strings to send to bot"""
    is_test = False

    print("Processing Started on...")
    pprint(data)

    is_test = data['data'].get('test', False)
    if is_test:
        test = "Test Webhook - Ignoring"
        print("Test Webhook - Ignoring")
        return test

    print("")
    print("Determinting payload type...")
    if isinstance(data, dict) and 'type' in data:
        payload_type = data['type']
        if not payload_type:
            print("Malformed Webhook - Type not found")
            return None
        if payload_type == 'userstory':
            print("Type is user story")
            processed_data = userstory_handler(data)
            return processed_data
    return

def userstory_handler(data):
    """Handle a user story webhook"""
    print("Userstory Webhook Received, Processing...")
    action = None
    if isinstance(data, dict) and 'action' in data:
        action = data['action']
        if not action:
            print("Malformed Webhook - Action not found")
            return None
    # Define variables
    # TODO: Play around with getting owner and setting them as the author of the original embed.
    # TODO: Assigned users and watchers.
    # TODO: @ mention watchers and assignee's
    # TODO: Update description emoji to match status' like closed or blocked.
    # TODO: Implement deleteing user stories handling.
    # TODO: Update blocker, Team Requirement, Client Requirement field text.
        # Need to build a database of user ID's and figure out discord @ing
    action_diff = []
    author = None                   # Check
    author_url = None               # Check
    author_icon_url = None          # Check
    assigned = None                 # Check
    blocked = None                  # Check
    blocked_reason = None           # Check
    description = None              # Check
    description_new = None          # Check
    description_second_part = None  # Check
    due_date = None                 # Check
    due_date_reason = None          # Check
    embed = None
    embed2 = None
    embed_color = None
    has_team_requirement = None     # Check
    has_client_requirement = None   # Check
    history = None                  # Check
    link = None                     # Check
    milestone = None                # Check
    status = None                   # Check
    status_old = None               # Check
    story_id = None                 # Check
    swimlane = None                 # Check
    swimlane_id = None              # Check
    tags = None                     # Check
    thread = None                   # Check
    title = None                    # Check
    title_linked = None             # Check
    title_plain = None              # Check
    to_from = {}
    thumbnail_url = None            # Check


    # Initial API call to catch pre-existing objects.
    if isinstance(data, dict) and 'data' in data:
        sub_data = data['data']
        if isinstance(sub_data, dict) and 'id' in sub_data:
            if sub_data['id']:
                story_id = sub_data['id']

    api_data = None
    retries = 3
    while api_data is None and retries > 0:
        api_data = get_user_story(data['data']['id'])
        if api_data is None and retries > 1:
            print(f"Retrying fetch user story... {retries-1} attempts remaining")
            time.sleep(1)
        else:
            print("User Story Fetched")
            if isinstance(api_data, dict) and 'swimlane' in api_data:
                swimlane_id = api_data['swimlane']
                api_data = get_swimlane(swimlane_id)
                swimlane = api_data['name']
                print(f"Swimlane: {swimlane}")
        retries -= 1

    if action == 'create' or action == 'change':
        # Get Title
        if isinstance(data, dict) and 'data' in data:
            sub_data = data['data']
            if isinstance(sub_data, dict) and 'assigned_to' in sub_data:
                assigned_to = sub_data['assigned_to']
                if not assigned_to:
                    assigned = "Unassigned"
                else:
                    assigned = assigned_to['full_name']
            if isinstance(sub_data, dict) and 'blocked_note' in sub_data:
                if sub_data['blocked_note']:
                    blocked_reason = sub_data['blocked_note']
                else:
                    blocked_reason = "No reason provided"
            if isinstance(sub_data, dict) and 'client_requirement' in sub_data:
                if not sub_data['client_requirement']:
                    has_client_requirement = False
                else:
                    has_client_requirement = True
            if isinstance(sub_data, dict) and 'description' in sub_data:
                print("Description field found")
                print("Description: " + sub_data['description'])
                description = sub_data['description']
            if isinstance(sub_data, dict) and 'due_date' in sub_data:
                if sub_data['due_date']:
                    due_date = sub_data['due_date']
                if sub_data['due_date_reason']:
                    due_date_reason = sub_data['due_date_reason']
            if isinstance(sub_data, dict) and 'id' in sub_data:
                if sub_data['id']:
                    story_id = sub_data['id']
                else:
                    print("Malformed Webhook - Story ID not found")
                    return None
            if isinstance(sub_data, dict) and 'is_blocked' in sub_data:
                if sub_data['is_blocked']:
                    blocked = True
                else:
                    blocked = False
            if isinstance(sub_data, dict) and 'milestone' in sub_data:
                if sub_data['milestone']:
                    milestone = sub_data['milestone']['name']
            if isinstance(sub_data, dict) and 'permalink' in sub_data:
                if sub_data['permalink']:
                    link = sub_data['permalink']
                else:
                    print("Malformed Webhook - Link not found")
                    return None
            if isinstance(sub_data, dict) and 'status' in sub_data:
                if sub_data['status']:
                    if sub_data['status']['name']:
                        status = sub_data['status']['name']
                    else:
                        print("Malformed Webhook - Status not found")
                        return None
            if isinstance(sub_data, dict) and 'subject' in sub_data:
                if sub_data['subject']:
                    title = sub_data['subject']
                else:
                    print("Malformed Webhook - Subject not found")
                    return None
            if isinstance(sub_data, dict) and 'tags' in sub_data:
                if sub_data['tags']:
                    tags = sub_data['tags']
                else:
                    tags = []
            if isinstance(sub_data, dict) and 'team_requirement' in sub_data:
                if sub_data['team_requirement']:
                    has_team_requirement = True
                else:
                    has_team_requirement = False
            if isinstance(sub_data, dict) and 'project' in sub_data:
                if sub_data['project']['logo_big_url']:
                    thumbnail_url = sub_data['project']['logo_big_url']
                else:
                    thumbnail_url = (
                        "https://pm.ks-webserver.com/v-1721729942015"
                        "/images/project-logos/project-logo-01.png"
                        )
        if isinstance(data, dict) and 'by' in data:
            author = data['by']['full_name']
            author_url = data['by']['permalink']
            if data['by']['photo']:
                author_icon_url = data['by']['photo']
            else:
                author_icon_url = (
                    "https://pm.ks-webserver.com/v-1721729942015"
                    "/images/user-avatars/user-avatar-01.png"
                    )

        title = data['data']['subject']
        story_url = data['data']['permalink']
        ticket_number = story_url.split('/')[-1]
        title_linked = f"[#{ticket_number} {title}]({story_url})"
        title_plain = f"#{ticket_number} {title}"

        if action == 'create':
            action_diff.append("A new user story was created")
            embed_color = discord.Color.green()
            api_data = None
            retries = 6
            while api_data is None and retries > 0:
                api_data = get_user_story(data['data']['id'])
                if api_data is None and retries > 1:
                    print(f"Retrying fetch user story... {retries-1} attempts remaining")
                    time.sleep(5)
                else:
                    print("User Story Fetched")
                    #pprint(api_data)
                    if isinstance(api_data, dict) and 'swimlane' in api_data:
                        swimlane_id = api_data['swimlane']
                        api_data = get_swimlane(swimlane_id)
                        swimlane = api_data['name']
                        print(f"Swimlane: {swimlane}")
                retries -= 1

        if action == 'change':
            if isinstance(data, dict) and 'change' in data:
                change = data['change']
                if isinstance(change, dict) and 'comment' in change:
                    if (
                        change['comment'] != '' and
                        change['edit_comment_date'] is None and
                        change['delete_comment_date'] is None
                        ):
                        print("Test change comment detection")
                        print(change['comment'])
                        action_diff.append("New Comment!")
                        embed_color = discord.Color.green()
                    elif (
                        change['comment'] is not None and
                        change['edit_comment_date'] is not None and
                        change['delete_comment_date'] is None
                        ):
                        action_diff.append("Comment edited.")
                        embed_color = discord.Color.blue()
                    elif (
                        change['comment'] is not None and
                        change['delete_comment_date'] is not None
                        ):
                        action_diff.append("Comment Deleted!")
                        embed_color = discord.Color.red()
                if isinstance(change, dict) and 'diff' in change:
                    diff = change['diff']
                    if isinstance(diff, dict) and 'description_diff' in diff:
                        if diff['description_diff'] == 'Check the history API for the exact diff':
                            history_retries = 6
                            while history is None and history_retries > 0:
                                history = (
                                get_user_story_history(user_story_id=data['data']['id'],
                                target_time=data['date'], time_threshold_ms=500)
                                )
                                if history is not None:
                                    break
                                history_retries -= 1
                    if history is not None:
                        api_diff = history.get('diff', {})
                        if isinstance(api_diff, dict) and 'description' in api_diff:
                            action_diff.append("The description was updated. "
                            "Check pinned for new description!")
                            description = api_diff['description'][1]
                            embed_color = discord.Color.blue()
                        else:
                            action_diff.append("Unknown Change was detected in the API")
                            print("Unknown change detected in the API")
                    if isinstance(diff, dict) and 'swimlane' in diff:
                        if isinstance(diff, dict) and 'to' in diff['swimlane']:
                            swimlane = diff['swimlane']['to']
                            action_diff.append("The swimlane was updated")
                    if isinstance(diff, dict) and 'status' in diff:
                        if isinstance(diff, dict) and 'from' in diff['status']:
                            status_old = diff['status']['from']
                            action_diff.append("The status was updated")
                            to_from['status'] = status
                            to_from['status_old'] = status_old
                            embed_color = discord.Color.blue()
            if action_diff:
                if (
                    action_diff[0] == "New Comment!" or
                    action_diff[0] == "Comment Deleted!" or
                    action_diff[0] == "Comment edited."
                    ):
                    action_diff.append(data['change']['comment'])

#    if len(action_diff) > 1:
#        print("Multiple changes detected")
#        action_diff = " & ".join(action_diff)
#        print(action_diff)
#    else:
#        print("Single change detected")
#        print(action_diff)

#    full_description = adjust_markdown(
#        f"# [#{ticket_number}]({story_url}) Description\n{description}")
    full_description = adjust_markdown(description)

    if len(full_description) > 2000:
        description = full_description[:1900]
        description = (":inbox_tray:\n\n" + description +
        "\n\n### Description Truncated. Log into Taiga to see full description."
        )
    else:
        description = ":inbox_tray:\n\n" + full_description

    # TODO: Get Swimlane # Figureout Swimlane ID from name
        # Figure out Discrod tag ID from name # Match Swimlane ID to Discord tag ID
#    userstory = Userstory(
#        action={"Action": action, "Diffs": action_diff},
#        assigned=assigned,
#        blocked={"Is Blocked": blocked, "Reason": blocked_reason},
#        description={"Description": description, "Description_second_part": second_part},
#        due_date={"Date": due_date, "Reason": due_date_reason},
#        has_client_requirement=has_client_requirement,
#        has_team_requirement=has_team_requirement,
#        link=link,
#        milestone=milestone,
#        status={"Current": status, "Old": status_old},
#        story_id=story_id,
#        tags={"Swimlane": swimlane, "Tags": tags},
#        title={"Plain": title_plain, "Linked": title_linked}
#    )
#    print("User Story Built")
#    pprint(userstory)

    if swimlane:
        swimlane_id = forum_tags.tags[swimlane]
    else:
        swimlane_id = None

    if (action == 'create') or (action == 'change'):
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
    if description_second_part:
        thread['description_second_part'] = description_second_part

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

    if action != 'create':
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
            name=author,
            url=author_url,
            icon_url=author_icon_url
            )
        embed.set_thumbnail(url=thumbnail_url)
        if to_from:
            embed.add_field(
                name="From",
                value=to_from['status_old'],
                inline=True
                )
            embed.add_field(
                name="To",
                value=to_from['status'],
                inline=True
                )
        embed.set_footer(
            text=title_plain,
            icon_url="https://taiga.io/media/images/Logo-text.width-140.png"
            )

    embed2 = discord.Embed(
        title=title_plain,
        description='Current Stauts (Always Updated)',
        url=link,
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now(datetime.UTC),
    )
    embed2.set_author(
        name=author,
        url=author_url,
        icon_url=author_icon_url
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
        name='Blocker',
        value=blocked_reason,
        inline=True
        )
    embed2.add_field(
        name='Team Requirement',
        value=has_team_requirement,
        inline=True
        )
    embed2.add_field(
        name='Client Requirement',
        value=has_client_requirement,
        inline=True
        )
    embed2.set_footer(
        text=title_plain,
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
        text=data['user_story'],
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
