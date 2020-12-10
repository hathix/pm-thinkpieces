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

from . import utilities

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

    # Start the index
    ix = index.create_in(WHOOSH_INDEX_DIR, schema)

    return ix


# Loads the search engine index from disk and returns it.
# Only works if you already called `build_new_index()` before.
def load_index():
    # Check if an index exists. If not, make one.
    # Obviously, has no effect if an index exists
    if not os.path.exists(WHOOSH_INDEX_DIR):
        build_new_index()

    # Now return what we have
    ix = index.open_dir(WHOOSH_INDEX_DIR)


def __main__():
    print("Hi")
