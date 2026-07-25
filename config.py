from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")
POKEMON_TOPIC=os.getenv("POKEMON_TOPIC")
ONEPIECE_TOPIC=os.getenv("ONEPIECE_TOPIC")
GIVEAWAY_TOPIC=os.getenv("GIVEAWAY_TOPIC")
NEWS_TOPIC=os.getenv("NEWS_TOPIC")
ANNOUNCEMENT_TOPIC=os.getenv("ANNOUNCEMENT_TOPIC")
print("BOT_TOKEN =", os.getenv("BOT_TOKEN"))
print("OWNER_ID =", os.getenv("OWNER_ID"))

OWNER_ID = int(os.getenv("OWNER_ID"))
