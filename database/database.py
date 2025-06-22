import motor.motor_asyncio
import base64
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta

# MongoDB connection
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
channels_collection = database["channels"]
encoded_links_collection = database["links"]
admins_collection = database["admins"]  # ✅ Added this line

# -------------------- User Functions --------------------

async def add_user(user_id: int):
    existing_user = await user_data.find_one({'_id': user_id})
    if existing_user:
        return
    try:
        await user_data.insert_one({'_id': user_id})
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def full_userbase():
    user_docs = user_data.find()
    return [doc['_id'] async for doc in user_docs]

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})

# -------------------- Admin Check --------------------

async def is_admin(user_id: int):
    return bool(await admins_collection.find_one({'_id': user_id}))

# -------------------- Channel Management --------------------

async def save_channel(channel_id: int):
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"channel_id": channel_id, "invite_link_expiry": None}},
        upsert=True
    )

async def get_channels():
    channels = await channels_collection.find().to_list(None)
    return [channel["channel_id"] for channel in channels]

async def delete_channel(channel_id: int):
    await channels_collection.delete_one({"channel_id": channel_id})

# -------------------- Link Encoding --------------------

async def save_encoded_link(channel_id: int):
    encoded_link = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"encoded_link": encoded_link, "status": "active"}},
        upsert=True
    )
    return encoded_link

async def get_channel_by_encoded_link(encoded_link: str):
    channel = await channels_collection.find_one({"encoded_link": encoded_link, "status": "active"})
    return channel["channel_id"] if channel else None

# -------------------- Request Link Encoding --------------------

async def save_encoded_link2(channel_id: int, encoded_link: str):
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"req_encoded_link": encoded_link, "status": "active"}},
        upsert=True
    )
    return encoded_link

async def get_channel_by_encoded_link2(encoded_link: str):
    channel = await channels_collection.find_one({"req_encoded_link": encoded_link, "status": "active"})
    return channel["channel_id"] if channel else None
