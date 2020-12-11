# Returns a list of all the RSS feeds that we'd like to track.
def get_feeds():
    # First, Substacks. Getting their RSS feeds is pretty simple/systematic.
    substack_domains = [
        "thegeneralist",
        "danco",
        "diff",
        "nbt",
        "platformer",
        "notboring",
        "sariazout",
        "digitalnative",
        "jamesonstartups",
        "breakingsmart",
        "artofgig",
        "theskip",
        "gwern",
        "productinsights"
    ]

    # Feeds are, e.g., https://thegeneralist.substack.com/feed
    substack_feeds = ["https://{0}.substack.com/feed".format(domain) for domain in substack_domains]

    # Now add some custom RSS feeds
    # Medium feeds are medium.com/feed/@user or medium.com/feed/publication
    custom_feeds = [
        "https://stratechery.com/feed/",
        "https://www.profgalloway.com/feed",
        "https://eugene-wei.squarespace.com/blog?format=rss",
        "https://kwokchain.com/feed",
        "https://medium.com/feed/@superwuster",
        "https://commoncog.com/blog/rss",
        "https://www.lennyrachitsky.com/feed",
        "https://medium.com/feed/bloated-mvp",
        "https://medium.com/feed/behavioral-economics-1",
        "https://daringfireball.net/feeds/main",
        "https://wongmjane.com/api/feed/rss",
        "https://fourweekmba.com/feed",
    ]

    # Unite all feeds into one
    all_feeds = substack_feeds + custom_feeds
    return all_feeds
