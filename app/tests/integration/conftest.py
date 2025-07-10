import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)
print("Loaded environment variables from .env.test")
table_names = ["reddit_posts", "reddit_comments", "reddit_tokens"]