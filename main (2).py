import asyncio
import os
from discord_bot import RTanksBot

async def main():
    # Get Discord bot token from environment
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
        return
    
    # Create and run the bot
    bot = RTanksBot()
    
    try:
        await bot.start(bot_token)
    except KeyboardInterrupt:
        print("\nShutting down bot...")
    except Exception as e:
        print(f"Error running bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
