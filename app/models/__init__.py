from sqlalchemy.orm import declarative_base

Base = declarative_base() # model base class

from .reddit_posts import RedditPosts
from .reddit_comments import RedditComments
from .reddit_tokens import RedditTokens
from .currency_prices import CurrencyPrices
from .reddit_sentiments import RedditSentiments
from .llm_providers import LlmProviders