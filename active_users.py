import os
import json
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set

def scan_logs_for_active_users(min_uses: int = 5) -> Dict[int, dict]:
    """
    Scan all log files in the logs directory and find users who used the bot at least min_uses times.

    Args:
        min_uses (int): Minimum number of times a user should have used the bot to be considered active

    Returns:
        Dict[int, dict]: Dictionary with user_id as key and user info as value
    """
    log_dir = "logs"
    user_activity = defaultdict(lambda: {"username": "", "search_count": 0, "last_active": None})

    # Scan all log files in the logs directory
    for filename in os.listdir(log_dir):
        if not filename.startswith("steel_bot_") or not filename.endswith(".log"):
            continue

        file_path = os.path.join(log_dir, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "Search activity:" in line:
                    try:
                        # Extract the JSON part of the log line
                        json_str = line.split("Search activity: ")[1].strip()
                        activity_data = json.loads(json_str)

                        user_id = activity_data["user_id"]
                        username = activity_data["username"]
                        timestamp = activity_data["timestamp"]

                        # Update user activity
                        user_activity[user_id]["username"] = username
                        user_activity[user_id]["search_count"] += 1

                        # Update last active timestamp if it's more recent
                        current_last_active = user_activity[user_id]["last_active"]
                        if current_last_active is None or timestamp > current_last_active:
                            user_activity[user_id]["last_active"] = timestamp

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logging.error(f"Error parsing log line: {e}")
                        continue

    # Filter for active users
    active_users = {
        user_id: info
        for user_id, info in user_activity.items()
        if info["search_count"] >= min_uses
    }

    return active_users

def save_active_users(active_users: Dict[int, dict], output_file: str = "active_users.json"):
    """
    Save active users to a JSON file.

    Args:
        active_users (Dict[int, dict]): Dictionary of active users
        output_file (str): Path to save the JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(active_users, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Find active users
    active_users = scan_logs_for_active_users(min_uses=5)

    # Save to file
    save_active_users(active_users)

    # Print summary
    print(f"\nFound {len(active_users)} active users:")
    for user_id, info in active_users.items():
        print(f"User ID: {user_id}")
        print(f"Username: {info['username']}")
        print(f"Search count: {info['search_count']}")
        print(f"Last active: {info['last_active']}")
        print("-" * 50)