# Utility module to fetch and parse news articles using newspaper3k

from loguru import logger
from newspaper import Article, ArticleException
from pydantic import HttpUrl

from core.models import ArticleContent


class ArticleFetcher:
    """Class to fetch and parse news articles from a given URL."""

    def __init__(self, url: HttpUrl):
        self.url = url

    def fetch_article(self) -> ArticleContent:
        """
        Fetch and parse the article title and text from the given URL.

        Returns:
            ArticleContent: The article content with title and text.
        """
        try:
            article = Article(str(self.url))
            article.download()
            article.parse()
            logger.info(f"Successfully fetched article from URL: {self.url}")
            return ArticleContent(title=article.title, text=article.text)
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
