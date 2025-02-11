"""
Handler for Taiga API calls
"""
from datetime import datetime, timedelta
import requests # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from config.config import TAIGA_BASE_URL  # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]
from handlers.taiga_api_auth import taiga_auth  # pylint: disable=import-error # pyright: ignore[reportMissingModuleSource]

def get_user_story_history(
    user_story_id,
    target_time=None,
    time_threshold_ms=500,
    limit=5,
    retries=3
    ):
    """Get user story history from Taiga API

    Args:
        user_story_id: value[int]: The ID of the user story
        target_time: Optional[value[str|datetime]]: Timestamp to filter history by
                Will return the entry closest to this timestamp
                If not provided, will return all history
            time_threshold_ms: Optional[value[int]]: Time threshold in milliseconds
                If target_time is provided, will return the entry 
                that is closest to target_time within this threshold
                default: 500ms
        limit: Optional[value[int]]: Number of entries to search and return
            default: 5
        retries: Optional[value[int]]: Number of retries if API call fails
            default: 3

    Returns:
        list: User story history if successful, None if failed
    """
    # If target_time is a string, parse it to datetime
    if isinstance(target_time, str):
        target_time = datetime.fromisoformat(target_time.replace('Z', '+00:00'))

    # Make request to get user story history with pagination
    history_url = (
        f"{TAIGA_BASE_URL}/api/v1/history/userstory/"
        f"{user_story_id}?page_size={limit}&order_by=-created_date"
        )

    history_data = generic_api_call(history_url, retries)

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
    return history_data if history_data else None


def get_user_story(user_story_id, retries=3):
    """Get a user story by ID from Taiga API

    Args:
        user_story_id: value[int]: The ID of the user story
        retries: Optional[int]: Number of retries if API call fails

    Returns:
        dict: User story data if successful, None if failed
    """
    url = f"{TAIGA_BASE_URL}/api/v1/userstories/{user_story_id}"

    return generic_api_call(url, retries)

def get_swimlane(swimlane_id, retries=3):
    """Get a swimlane by ID from Taiga API

    Args:
        swimlane_id: value[int]: The ID of the swimlane
        retries: Optional[int]: Number of retries if API call fails

    Returns:
        dict: Response data if successful, None if failed
    """
    url = f"{TAIGA_BASE_URL}/api/v1/swimlanes/{swimlane_id}"

    return generic_api_call(url, retries)

def get_headers():
    """Get headers with valid authentication token"""
    token = taiga_auth.get_token()
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def generic_api_call(url, retries=3):
    """Make a generic API call to Taiga API

    Args:
        url: Value[str]: The URL to call
            Full url should be provided i.e. 
                https://taiga.example.com/api/v1/userstories/172
        retries: Optional[int]: Number of retries if API call fails

    Returns:
        dict: Response data if successful, None if failed
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        if response.status_code != 200:
            while retries > 0:
                print(f"Taiga auth token: {taiga_auth.token}")
                print(f"Retrying API call (attempt {3 - retries + 1})...")
                response.status_code = None
                response = requests.get(url, headers=get_headers(), timeout=30)
                print(f"response.status_code: {response.status_code}")
                if response.status_code == 401:
                    try:
                        auth_token = taiga_auth.get_token()
                        taiga_auth.token = auth_token
                        retries -= 1
                    except (requests.RequestException, ValueError, KeyError) as e:
                        print(f"Error with API token: {e}")
                        retries -= 1
                elif response.status_code != 200:
                    retries -= 1
                else:
                    return response.json()
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching: {e}")
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
