import requests
from datetime import datetime, timedelta
from config import TAIGA_BASE_URL, TAIGA_AUTH_TOKEN

def get_user_story_history(user_story_id, target_time=None, time_threshold_ms=500, limit=20):
    # If target_time is a string, parse it to datetime
    if isinstance(target_time, str):
        target_time = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
    """
    Get the history of a user story from Taiga API
    
    Args:
        user_story_id (int): The ID of the user story
        target_time (datetime): Target time to search around (default: None)
        time_threshold_ms (int): Time threshold in milliseconds (default: 500)
        limit (int): Maximum number of history entries to fetch (default: 20)
        
    Returns:
        list: Filtered history data if successful, None if failed
    """
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {TAIGA_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Make request to get user story history with pagination
    history_url = f"{TAIGA_BASE_URL}/api/v1/history/userstory/{user_story_id}?page_size={limit}&order_by=-created_date"
    
    try:
        response = requests.get(history_url, headers=headers)
        response.raise_for_status()
        history_data = response.json()

        if target_time:
            # Convert threshold to timedelta
            threshold = timedelta(milliseconds=time_threshold_ms)
            
            # Filter results by time threshold
            filtered_history = []
            print(f"Target time: {target_time}")
            print(f"Threshold: {threshold}")
            
            for entry in history_data:
                entry_time = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
                time_diff = abs(entry_time - target_time)
                
#                print(f"Entry time: {entry_time}")
#                print(f"Time difference: {time_diff}")
#                print(f"Within threshold? {time_diff <= threshold}\n")
                
                if time_diff <= threshold:
                    filtered_history.append(entry)
            
            return filtered_history
        
        return history_data

    except requests.exceptions.RequestException as e:
        print(f"Failed to get user story history: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    story_id = 89  # Replace with actual user story ID
    
    # Example with time filtering
    # Example timestamp from Taiga webhook
    target_time = '2025-02-08T20:45:03.073Z'
    history = get_user_story_history(
        story_id,
        target_time=target_time,
        time_threshold_ms=500
    )
    
    if history:
        print("User Story History:")
        for entry in history:
            entry_time = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
            print(f"- Time: {entry_time}")
            print(f"  Type: {entry.get('type', '')}")
            print(f"  Comment: {entry.get('comment', '')}")
            print(f"  Values Changed: {entry.get('diff', {})}\n")
