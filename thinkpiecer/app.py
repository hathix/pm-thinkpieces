from flask import Flask
from flask import render_template
from flask.json import jsonify

import thinkpiecer
import utilities
import feeds

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/build')
def build():
    ## Build the search index and fill it with articles

    # TODO: takes really long so Heroku might time out (we get like 30s)

    # Wipe the index and create a clean one
    ix = thinkpiecer.build_new_index()

    # Get feeds to read and insert
    feed_list = feeds.get_feeds()

    # This adds any new articles we find
    # to the index, while leaving existing
    # ones untouched. (Now it doesn't duplicate!)
    thinkpiecer.add_articles_to_index(feed_list, ix)

    return 'Built Index!!'


@app.route('/search/<query>')
def search(query):
    # Run a search for the given term and print results

    # Load the index (or make a blank one if it's not there)
    # If the index is already there, this will be a LOT faster.
    ix = thinkpiecer.load_index()

    hits = thinkpiecer.search(query, ix)

    # Render template
    return render_template('search.html', results=hits)
    # return jsonify(hits)
