import os
import json
import asyncio
import logging
from typing import List, Dict
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

# Load environment variables
load_dotenv()

async def send_message_to_users(bot: Bot, user_ids: List[int], message: str) -> Dict[int, bool]:
    """
    Send a message to multiple users and track success/failure.

    Args:
        bot (Bot): Initialized aiogram Bot instance
        user_ids (List[int]): List of user IDs to send message to
        message (str): Message to send

    Returns:
        Dict[int, bool]: Dictionary with user_id as key and success status as value
    """
    results = {}

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message)
            results[user_id] = True
            logging.info(f"Successfully sent message to user {user_id}")
        except TelegramBadRequest as e:
            if "user not found" in str(e).lower():
                logging.warning(f"User {user_id} not found or blocked the bot")
            else:
                logging.error(f"Failed to send message to user {user_id}: {e}")
            results[user_id] = False
        except Exception as e:
            logging.error(f"Unexpected error sending message to user {user_id}: {e}")
            results[user_id] = False

        # Add a small delay between messages to avoid rate limiting
        await asyncio.sleep(0.1)

    return results

async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Load active users
    try:
        with open("active_users.json", 'r', encoding='utf-8') as f:
            active_users = json.load(f)
    except FileNotFoundError:
        logging.error("active_users.json not found. Please run active_users.py first.")
        return

    # Initialize bot
    bot = Bot(token=os.getenv("BOT_TOKEN"))

    # Example message - you can modify this or make it interactive
    message = """🔔 Important Update!

We've added new features to the Steel Bot:
- Improved search accuracy
- New steel grades database
- Faster response times

Try it out now with /find command!"""

    # Get list of user IDs
    user_ids = list(active_users.keys())

    # Send messages
    results = await send_message_to_users(bot, user_ids, message)

    # Print summary
    successful = sum(1 for success in results.values() if success)
    print(f"\nMessage sending summary:")
    print(f"Total users: {len(user_ids)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(user_ids) - successful}")

    # Close bot session
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())