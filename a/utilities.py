# Utility functions

# Convenience function to safely get an item from a dict.
# If the key doesn't exist, just returns none
def safe_get(obj, key):
    if obj.has_key(key):
        return obj[key]
    else:
        return None
