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
import utilities
from utilities import safe_get
import feeds

# Constants
WHOOSH_INDEX_DIR = "../whoosh_index3"



# Creates a brand-new index and returns it.
# This deletes the currently-existing index!
def build_new_index():
    # Start by making a new schema.
    # This is stored with the index.

    # First, get an addon that lets users run optional case-sensitive searches.
    case_sensitive_analyzer = utilities.get_case_sensitive_analyzer()

    schema = Schema(
        title=TEXT(stored=True),
        author=TEXT(stored=True),
        publication=TEXT(stored=True),
        summary=TEXT(stored=True),
        url=ID(stored=True, unique=True),
        published=DATETIME(stored=True),
        content=TEXT(stored=True, analyzer=case_sensitive_analyzer))

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

            # This ensures that we don't have duplicate entries with the same unique key (here, URL).
            # If the key already exists, this wipes it out
            # and replaces it with a fresh entry.
            # If the key doesn't exist, it creates
            # from scratch.
            # TODO: i don't think it works, check
            writer.update_document(
                title=safe_get(entry, 'title'),
                author=safe_get(entry, 'author'),
                publication=publication,
                summary=safe_get(entry, 'summary'),
                url=safe_get(entry, 'link'),
                published=clean_datetime,
                content=body_text)

    print("DONE!")
    writer.commit()

# Given an index and a search term,
# returns details on all matched articles.
def search(search_term, ix):
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)
        # Allow fuzzy matching (EDIT: kinda screws things up)
        # parser.add_plugin(FuzzyTermPlugin())
        # Allow searching for entire phrases w/ single quotes, like 'microsoft teams'
        parser.add_plugin(qparser.SingleQuotePlugin())

        query = parser.parse(search_term)
        results = searcher.search(query, limit=None)

        # Highlighting settings
        # This provides more context characters around the searched-for text
        results.fragmenter.surround = 50
        results.fragmenter.maxchars = 500

        # Surround matched tags with brackets
        # results.formatter = utilities.BracketFormatter()

        # This just prints it nicely for the terminal output
        # for hit in results:
        #     print(hit['title'])
        #     print(hit['publication'])
        #     print(hit['author'])
        #     print(hit['url'])
        #     print(hit.highlights("content", top=3))
        #     print("\n")

        # Now we actually compute a dict of results and return it
        # Convert each Hit into a dict
        def extract_hit_info(hit):
            # dict.get() is safer than the [bracket] notation since it doesn't
            # error out if the key doesn't exist; it just returns None
            return {
                'title': hit.get('title'),
                'publication': hit.get('publication'),
                'author': hit.get('author'),
                'url': hit.get('url'),
                'published': hit.get('published'),
                'highlights': hit.highlights("content", top=3),
                'score': hit.score
            }

        hit_list = [extract_hit_info(h) for h in results]
        return hit_list


def main():
    # Call build() the first time, then load()
    # every time thereafter
    # ix = build_new_index()
    ix = load_index()

    feed_list = feeds.get_feeds()

    # This adds any new articles we find
    # to the index, while leaving existing
    # ones untouched. (Now it doesn't duplicate!)
    add_articles_to_index(feed_list, ix)

    # Stress-test: run this many times and see if it's idempotent
    # add_articles_to_index(feed_list, ix)

    # Demo
    print(search("Airtable", ix))


if __name__ == '__main__': main()
