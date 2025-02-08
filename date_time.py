from datetime import datetime
import pytz


def resolve(timestamp):

    # Parse the ISO 8601 format string and remove 'Z'
    dt = datetime.strptime(timestamp[:-1], '%Y-%m-%dT%H:%M:%S.%f')

    # Convert to Eastern Time (EDT)
    eastern = pytz.timezone('America/New_York')
    dt = dt.replace(tzinfo=pytz.utc).astimezone(eastern)

    # Format to human-readable string
    human_readable = dt.strftime("%B %dth %Y at %I:%M%p %Z")

    # Replace 'th' with appropriate suffix
    day_suffix = 'th' if 4 <= dt.day <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(dt.day % 10, 'th')
    human_readable = human_readable.replace('th', day_suffix)

    return human_readable
