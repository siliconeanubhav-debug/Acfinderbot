import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# India Standard Timezone Fix
IST = ZoneInfo("Asia/Kolkata")

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.users = self.db["users"]
        self.posts = self.db["posts"]

    async def add_user(self, user_id: int, name: str):
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$set": {"user_id": int(user_id), "name": name}},
            upsert=True
        )

    async def make_premium(self, user_id: int, duration_td: timedelta = None):
        """Adds premium status to user with optional duration in Asia/Kolkata time."""
        expiry_date = datetime.now(IST) + duration_td if duration_td else None
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$set": {"is_premium": True, "premium_expiry": expiry_date}},
            upsert=True
        )

    # Alias method so both make_premium and add_premium work without crashing
    async def add_premium(self, user_id: int, duration_td: timedelta = None):
        await self.make_premium(user_id, duration_td)

    async def remove_premium(self, user_id: int):
        """Removes premium status from user."""
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$set": {"is_premium": False, "premium_expiry": None}},
            upsert=True
        )

    async def is_premium_user(self, user_id: int) -> bool:
        """Checks if user is premium with IST Timezone awareness and auto-expiration."""
        user = await self.users.find_one({"user_id": int(user_id)})
        if not user or not user.get("is_premium", False):
            return False

        expiry = user.get("premium_expiry")
        if expiry:
            # Handle naive datetime conversion from MongoDB
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=IST)
            
            # Check against current IST time
            if datetime.now(IST) > expiry:
                await self.remove_premium(user_id)
                return False

        return True

    async def add_post(self, title: str, link: str):
        # USER RULE: Save only the first line as the searchable title
        first_line = title.split("\n")[0].strip()
        await self.posts.insert_one({"title": first_line, "link": link})

    async def search_posts(self, query: str, limit: int = 5):
        regex_pattern = re.compile(re.escape(query), re.IGNORECASE)
        return await self.posts.find({"title": {"$regex": regex_pattern}}).to_list(length=limit)

    async def get_all_posts(self):
        """Fetches all stories/posts for fuzzy search matching."""
        try:
            return await self.posts.find().to_list(length=None)
        except Exception as e:
            print(f"Database Fetch Error: {e}")
            return []

    async def delete_post(self, title: str) -> bool:
        """Deletes a post/story from the database by title (Case-Insensitive)."""
        first_line = title.split("\n")[0].strip()
        
        # Exact match first
        result = await self.posts.delete_one({"title": first_line})
        if result.deleted_count > 0:
            return True
            
        # Fallback: Case-insensitive regex match
        regex_pattern = re.compile(f"^{re.escape(first_line)}$", re.IGNORECASE)
        regex_result = await self.posts.delete_one({"title": {"$regex": regex_pattern}})
        if regex_result.deleted_count > 0:
            return True

        # Partial Regex Match as last resort
        partial_pattern = re.compile(re.escape(first_line), re.IGNORECASE)
        partial_result = await self.posts.delete_one({"title": {"$regex": partial_pattern}})
        return partial_result.deleted_count > 0

    async def delete_post_by_link(self, link: str) -> bool:
        """Deletes a post/story by link directly."""
        result = await self.posts.delete_one({"link": link.strip()})
        return result.deleted_count > 0

db = Database()
