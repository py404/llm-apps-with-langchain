# Utility module to fetch and parse news articles using newspaper3k

from loguru import logger
from newspaper import Article, ArticleException
from pydantic import HttpUrl


class ArticleFetcher:
    """Class to fetch and parse news articles from a given URL."""

    def __init__(self, url: HttpUrl):
        self.url = url

    def fetch_article(self) -> str:
        """
        Fetch and parse the article text from the given URL.

        Returns:
            str: The cleaned article text.
        """
        try:
            article = Article(self.url)
            article.download()
            article.parse()
            logger.info(f"Successfully fetched article from URL: {self.url}")
            return article.text
        except ArticleException as e:
            logger.error(
                f"ArticleException while fetching article from URL: {self.url}"
            )
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Failed to fetch article from {self.url}")
            logger.error(e)
            raise
