from whoosh import highlight, analysis

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


# Allows optional case-sensitive searches. all-lowercase is case insensitive,
# any capital letters makes it case sensitive
class CaseSensitivizer(analysis.Filter):
    def __call__(self, tokens):
        for t in tokens:
            yield t
            if t.mode == "index":
               low = t.text.lower()
               if low != t.text:
                   t.text = low
                   yield t

# Builds an analyzer you can actually use. Feed it in when building a schema.
# This makes queries case-sensitive when Uppercase text is used, but
# case-insensitive when it's all lower-case
def get_case_sensitive_analyzer():
    return analysis.RegexTokenizer() | CaseSensitivizer()
