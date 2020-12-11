from flask import Flask
from flask import render_template
from flask import request
from flask.json import jsonify
import os

import thinkpiecer
import utilities
import feeds


app = Flask(__name__)

def main():
    # Set up to run on the proper port
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/test')
def testr():
    return 'Sup!'


# Hide this from the public!
# Building and updating the index is now done with our own scripts
# @app.route('/build')
# def build():
#     ## Build the search index and fill it with articles
#
#     # TODO: takes really long so Heroku might time out (we get like 30s)
#
#     # Wipe the index and create a clean one
#     ix = thinkpiecer.build_new_index()
#
#     # Get feeds to read and insert
#     feed_list = feeds.get_feeds()
#
#     # This adds any new articles we find
#     # to the index, while leaving existing
#     # ones untouched. (Now it doesn't duplicate!)
#     thinkpiecer.add_articles_to_index(feed_list, ix)
#
#     return 'Built Index!!'


# @app.route('/search/<query>')
# def search(query):
#     # Run a search for the given term and print results
#
#     # Load the index (or make a blank one if it's not there)
#     # If the index is already there, this will be a LOT faster.
#     ix = thinkpiecer.load_index()
#
#     hits = thinkpiecer.search(query, ix)
#
#     # Render template
#     return render_template('search.html', results=hits)
#     # return jsonify(hits)

@app.route('/search', methods=['GET'])
def search():
    # Run a search for the given term and print results

    # Get query from GET params
    query = request.args.get('query', '');

    # Load the index (or make a blank one if it's not there)
    # If the index is already there, this will be a LOT faster.
    ix = thinkpiecer.load_index()

    hits = thinkpiecer.search(query, ix)

    # Render template
    return render_template('search.html', results=hits, query=query)
    # return jsonify(hits)


## Custom Jinja filters

# Nice way to format a datetime
@app.template_filter('datetime')
def format_datetime(value):
    return value.strftime("%b %d, %Y")
