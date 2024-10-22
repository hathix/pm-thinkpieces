import feedparser
from bs4 import BeautifulSoup
from whoosh import index
from whoosh.fields import *
from whoosh.writing import AsyncWriter
from whoosh.qparser import QueryParser
import whoosh.qparser as qparser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh import highlight
import calendar
from datetime import datetime
import os, os.path

# Local modules
import utilities
from utilities import safe_get
import feeds

## Constants

# For dev work
# WHOOSH_INDEX_DIR = "./whoosh_index3"

# For deployment to prod
WHOOSH_INDEX_DIR = "./whoosh_prod"


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
        description=TEXT(stored=True),
        url=ID(stored=True, unique=True),
        published=DATETIME(stored=True, sortable=True),
        content=TEXT(stored=True, analyzer=case_sensitive_analyzer),
        content_word_count=NUMERIC(stored=True))

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
    # Let's use AsyncWriter, which is a thread-safe, straight upgrade
    # to the normal one
    # https://whoosh.readthedocs.io/en/latest/api/writing.html#whoosh.writing.AsyncWriter
    # writer = ix.writer()
    writer = AsyncWriter(ix)

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
            clean_datetime = None
            if entry.get('published_parsed') is not None:
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

            # Clean up the description too. This is usually the subheading
            # but sometimes contains a ton of content.
            description = None
            raw_description = entry.get('description')
            if raw_description is not None:
                description_tree = BeautifulSoup(raw_description, features="html.parser")
                description = description_tree.get_text(" ", strip=True)

            # Measure how many words are in the body text
            word_count = utilities.word_count(body_text)

            writer.update_document(
                title=safe_get(entry, 'title'),
                author=safe_get(entry, 'author'),
                publication=publication,
                summary=safe_get(entry, 'summary'),
                description=description,
                url=safe_get(entry, 'link'),
                published=clean_datetime,
                content=body_text,
                content_word_count=word_count)

    print("DONE!")
    writer.commit()

# Given an index and a search term,
# returns details on all matched articles.
def search(search_term, ix):
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)

        # Allow fuzzy matching to catch misspellings
        # Really slows things down, and requires a "~" in the query which nobody will do
        # parser.add_plugin(qparser.FuzzyTermPlugin())

        # Allow searching for entire phrases w/ single quotes, like 'microsoft teams'
        parser.add_plugin(qparser.SingleQuotePlugin())

        query = parser.parse(search_term)
        # May need to tweak the limit here. Higher = slower, but more thorough
        # (though I think 20 is plenty)
        results = searcher.search(query, limit=20)

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


# Returns a reverse-chronological list of recent articles from
# our chosen feeds. Good for making a browsable feed.
def get_recent_articles(ix):
    with ix.searcher() as searcher:
        # Search for the newest items.
        # We have to search for SOMETHING so let's filter out all the
        # articles that are too short (thus, they're likely paywalled or
        # programming notes or random Medium replies). Then we can sort by date desc.
        parser = QueryParser("content_word_count", ix.schema)

        # Add a parser to do numerical comparisons
        # This is the "greater than, less than" plugin
        # I've found that the articles that are too short tend to be <250 words
        # (Medium responses are like 10-20 words, paywalled Substack is like 60,
        # random programming notes tend to be 100-200). So filter those out.
        THINKPIECE_MIN_WORD_COUNT = 250
        parser.add_plugin(qparser.GtLtPlugin())
        search_term = "content_word_count:>={0}".format(THINKPIECE_MIN_WORD_COUNT)
        query = parser.parse(search_term)

        results = searcher.search(query,
            limit=50, sortedby="published", reverse=True)

        # Convert each Hit into a dict
        def extract_hit_info(hit):
            # We don't have highlights from Whoosh, so let's use the description
            # (usually the subheader) from the RSS feed.
            # Some newsletters put their ENTIRE content in the description; in
            # that case, chop it off
            preview = None
            PREVIEW_LENGTH_CHARS = 300

            # description = hit.get('description')
            # if description is not None:
            #     if len(description) > PREVIEW_LENGTH_CHARS:
            #         # They put their ENTIRE piece in here, probably, so truncate
            #         preview = description[:PREVIEW_LENGTH_CHARS] + "..."
            #     else:
            #         # Like normal, they just used a short subheading. Include
            #         # all of it
            #         preview = description

            # EDIT: the descriptions are often kinda lame. Let's use the
            # beginning of the content instead.
            if hit.get('content') is not None:
                preview = hit.get('content')[:PREVIEW_LENGTH_CHARS] + "..."

            return {
                'title': hit.get('title'),
                'publication': hit.get('publication'),
                'author': hit.get('author'),
                'url': hit.get('url'),
                'published': hit.get('published'),
                'preview': preview,
                # 'content_word_count': hit.get('content_word_count'),
                'score': hit.score
            }

        hit_list = [extract_hit_info(h) for h in results]
        return hit_list


# Rebuilds the entire index from scratch, including adding
# all the documents.
def build_from_scratch():
    # Make an index
    ix = build_new_index()

    # Get and add feeds
    feed_list = feeds.get_feeds()
    add_articles_to_index(feed_list, ix)

    print("Built!")


# Loads the existing index and adds articles to it.
# This is idempotent -- doesn't affect any existing articles.
def update_index():
    # Load the existing index (if none exists, make a new one, in which case
    # this function behaves the same as build_from_scratch())
    ix = load_index()

    # Get and add feeds
    feed_list = feeds.get_feeds()
    add_articles_to_index(feed_list, ix)

    print("Updated!")


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
