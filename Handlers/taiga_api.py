"""
Handler for Taiga API calls
"""
from datetime import datetime, timedelta
import requests # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from config import TAIGA_BASE_URL
from Handlers.taiga_api_auth import taiga_auth

def get_user_story_history(user_story_id, target_time=None, time_threshold_ms=500, limit=5):
    """Get user story history from Taiga API"""
    # If target_time is a string, parse it to datetime
    if isinstance(target_time, str):
        target_time = datetime.fromisoformat(target_time.replace('Z', '+00:00'))

    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {taiga_auth.auth_token}",
        "Content-Type": "application/json"
    }

    # Make request to get user story history with pagination
    history_url = (
        f"{TAIGA_BASE_URL}/api/v1/history/userstory/"
        f"{user_story_id}?page_size={limit}&order_by=-created_date"
        )

    try:
        response = requests.get(history_url, headers=headers, timeout=30)
        response.raise_for_status()
        history_data = response.json()

        if target_time:
            # Convert threshold to timedelta
            threshold = timedelta(milliseconds=time_threshold_ms)

            # Find the entry closest to target_time within threshold
            closest_entry = None
            min_time_diff = threshold

            for entry in history_data:
                entry_time = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
                time_diff = abs(entry_time - target_time)

                if time_diff <= threshold and time_diff <= min_time_diff:
                    closest_entry = entry
                    min_time_diff = time_diff

            return closest_entry

        # If no target_time specified, return the most recent entry
        return history_data[0] if history_data else None

    except requests.exceptions.RequestException as e:
        print(f"Failed to get user story history: {e}")
        return None

def get_user_story(user_story_id):
    """Get a user story by ID from Taiga API

    Args:
        user_story_id (int): The ID of the user story

    Returns:
        dict: User story data if successful, None if failed
    """
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {taiga_auth.auth_token}",
        "Content-Type": "application/json"
    }

    # Make request to get user story
    story_url = f"{TAIGA_BASE_URL}/api/v1/userstories/{user_story_id}"

    try:
        response = requests.get(story_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user story: {e}")
        return None

def get_swimlane(swimlane_id):
    """Get a swimlane by ID from Taiga API

    Args:
        swimlane_id (int): The ID of the swimlane

    Returns:
        dict: Response data if successful, None if failed
    """
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {taiga_auth.auth_token}",
        "Content-Type": "application/json"
    }

    # Make request to get user story
    url = f"{TAIGA_BASE_URL}/api/v1/swimlanes/{swimlane_id}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching swimlane: {e}")
        return None

def generic_api_call(endpoint, data=None):
    """Make a generic API call to Taiga API

    Args:
        endpoint (str): The endpoint to call
        data (dict, optional): Data to send in the request

    Returns:
        dict: Response data if successful, None if failed
    """
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {taiga_auth.auth_token}",
        "Content-Type": "application/json"
    }

    # Make request to get user story
    url = f"{TAIGA_BASE_URL}{endpoint}"

    try:
        response = requests.get(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user story: {e}")
        return None


#if __name__ == "__main__":
#    # Example usage
#    story_id =266   # Replace with actual user story ID
#
#    # Example with time filtering
#    # Example timestamp from Taiga webhook
#    target_time = '2025-02-08T20:45:03.073Z'
#    history = get_user_story_history(
#        story_id,
#        target_time=target_time,
#        time_threshold_ms=500
#    )
#
#    if history:
#        print("User Story History:")
#        for entry in history:
#            entry_time = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
#            print(f"- Time: {entry_time}")
#            print(f"  Type: {entry.get('type', '')}")
#            print(f"  Comment: {entry.get('comment', '')}")
#            print(f"  Values Changed: {entry.get('diff', {})}\n")
