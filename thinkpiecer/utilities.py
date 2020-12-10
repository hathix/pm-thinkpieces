from whoosh import highlight

##### Utility functions here

# Convenience function to safely get an item from a dict.
# If the key doesn't exist, just returns none
def safe_get(obj, key):
    if obj.has_key(key):
        return obj[key]
    else:
        return None

# A new formatter for Whoosh search results.
class BracketFormatter(highlight.Formatter):
    """Puts square brackets around the matched terms.
    """

    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the
        # token
        tokentext = highlight.get_text(text, token, replace)

        # Return the text as you want it to appear in the highlighted
        # string
        return "[[%s]]" % tokentext
