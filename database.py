import re
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

    async def make_premium(self, user_id: int):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_premium": True}}, upsert=True)

    async def remove_premium(self, user_id: int):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_premium": False}}, upsert=True)

    async def is_premium_user(self, user_id: int) -> bool:
        user = await self.users.find_one({"user_id": user_id})
        return user.get("is_premium", False) if user else False

    async def add_post(self, title: str, link: str):
        # Save only the first line as the searchable title
        first_line = title.split("\n")[0].strip()
        await self.posts.insert_one({"title": first_line, "link": link})

    async def search_posts(self, query: str, limit: int = 5):
        regex_pattern = re.compile(re.escape(query), re.IGNORECASE)
        return await self.posts.find({"title": {"$regex": regex_pattern}}).to_list(length=limit)

db = Database()
