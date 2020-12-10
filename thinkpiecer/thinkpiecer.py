import feedparser
from bs4 import BeautifulSoup
from whoosh import index
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.qparser as qparser
from whoosh import highlight
import calendar
from datetime import datetime
import os, os.path

# Local modules
from utilities import safe_get
import feeds

# Constants
WHOOSH_INDEX_DIR = "../whoosh_index3"



# Creates a brand-new index and returns it.
# This deletes the currently-existing index!
def build_new_index():
    # Start by making a new schema.
    # This is stored with the index.
    schema = Schema(
        title=TEXT(stored=True),
        author=TEXT(stored=True),
        publication=TEXT(stored=True),
        summary=TEXT(stored=True),
        url=TEXT(stored=True),
        published=DATETIME(stored=True),
        content=TEXT(stored=True))

    # Create a home for the index if it doesn't exist already
    if not os.path.exists(WHOOSH_INDEX_DIR):
        os.mkdir(WHOOSH_INDEX_DIR)

    # Create the index
    ix = index.create_in(WHOOSH_INDEX_DIR, schema)
    return ix


# Loads the search engine index from disk and returns it.
# If no index exists, creates a brand-new one.
# (if you have an index you want to overwrite,
# call build_new_index again)
def load_index():
    # Check if an index exists. If not, make one.
    # Obviously, has no effect if an index exists
    if not os.path.exists(WHOOSH_INDEX_DIR):
        build_new_index()

    # Now return what we have
    ix = index.open_dir(WHOOSH_INDEX_DIR)
    return ix


# Given a list of RSS feeds and an index
# (either new or existing), scrapes the list of
# entries from the RSS feeds and adds them to the index
# so we can search them.
def add_articles_to_index(feed_list, ix):
    # Create a writer to start adding entries
    writer = ix.writer()

    for feed_url in feed_list:
        print(feed_url)
        news_feed = feedparser.parse(feed_url)

        # NOTE: we can only get the last few entries from this RSS feed.
        # Substack doesn't seem to show anything older than the last 20.
        # So we should build in a system to start caching these.

        for entry in news_feed.entries:

            # Get publication name. This is in the feed's `feed` field, along with other metadata
            publication = None
            metadata = safe_get(news_feed, 'feed')
            if metadata is not None:
                publication = safe_get(metadata, 'title')

            # Clean up the date into a normal datetime
            clean_datetime = datetime.fromtimestamp(calendar.timegm(entry['published_parsed']))

            # Most feeds put the main content in `content`,
            # but a rare few like Eugene Wei put it in `summary`
            # (in which case `content` is empty). With this logic, let's get a single `content` field.
            body_text = None
            # See if `content` exists
            content_holder = safe_get(entry, 'content')
            if content_holder is not None:
                # We have content; fill it in
                content_tree = BeautifulSoup(content_holder[0]['value'], features="html.parser")
                body_text = content_tree.get_text(" ", strip=True)
            else:
                # No content provided. `summary` must hold all the text.
                summary_tree = BeautifulSoup(safe_get(entry, 'summary'), features="html.parser")
                body_text = summary_tree.get_text(" ", strip=True)

            writer.add_document(
                title=safe_get(entry, 'title'),
                author=safe_get(entry, 'author'),
                publication=publication,
                summary=safe_get(entry, 'summary'),
                url=safe_get(entry, 'link'),
                published=clean_datetime,
                content=body_text)

    print("DONE!")
    writer.commit()


def main():
    ix = load_index()
    feed_list = feeds.get_feeds()
    add_articles_to_index(feed_list, ix)


if __name__ == '__main__': main()
