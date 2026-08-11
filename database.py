import re
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.users = self.db["users"]
        self.posts = self.db["posts"]

    async def add_user(self, user_id: int, name: str):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "name": name}},
            upsert=True
        )

    async def add_premium(self, user_id: int, duration_td: timedelta = None):
        """Adds premium status to user with optional duration (e.g. 1d, 12h, 30m)."""
        expiry_date = datetime.now() + duration_td if duration_td else None
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": True, "premium_expiry": expiry_date}},
            upsert=True
        )

    async def remove_premium(self, user_id: int):
        """Removes premium status from user."""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": False, "premium_expiry": None}},
            upsert=True
        )

    async def is_premium_user(self, user_id: int) -> bool:
        """Checks if user is premium and auto-expires premium if time is over."""
        user = await self.users.find_one({"user_id": user_id})
        if not user or not user.get("is_premium", False):
            return False

        expiry = user.get("premium_expiry")
        if expiry and datetime.now() > expiry:
            # Auto-expire premium if time passed
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
        """Deletes a post/story from the database by title."""
        first_line = title.split("\n")[0].strip()
        result = await self.posts.delete_one({"title": first_line})
        return result.deleted_count > 0

db = Database()
