# Returns a list of all the RSS feeds that we'd like to track.
def get_feeds():
    # First, Substacks. Getting their RSS feeds is pretty simple/systematic.
    substack_domains = [
        # Generic
        "thegeneralist",
        "danco",
        "diff",
        "nbt",
        "platformer",
        "notboring",
        "sariazout",
        "digitalnative",
        "jamesonstartups",
        "napkinmath",
        # "breakingsmart",
        # "artofgig",
        # "theskip",
        "productinsights",
        "adventurecapital",
        "diane", # this is called "Snapshots" and has snapshots of the industry

        # HealthTech
        "insilico",
        "caseload",
        "theprescription",

        # EdTech
        "meganoconnor",

        # Emerging Markets
        "emerging",
        "lillianli",
        "hind",

        # Enterprise
        "natjin",
    ]

    # Feeds for Substacks are, e.g., https://thegeneralist.substack.com/feed
    substack_feeds = ["https://{0}.substack.com/feed".format(domain) for domain in substack_domains]

    # Now add some custom RSS feeds
    # Medium feeds are medium.com/feed/@user or medium.com/feed/publication
    custom_feeds = [
        # Generic
        "https://stratechery.com/feed/",
        "http://ben-evans.com/benedictevans?format=rss",
        "https://www.profgalloway.com/feed",
        "https://eugene-wei.squarespace.com/blog?format=rss",
        "https://kwokchain.com/feed",
        "https://medium.com/feed/@superwuster",
        # "https://commoncog.com/blog/rss",
        "https://www.lennyrachitsky.com/feed",
        "https://medium.com/feed/bloated-mvp",
        "https://medium.com/feed/behavioral-economics-1",
        # "https://daringfireball.net/feeds/main",
        "https://wongmjane.com/api/feed/rss",
        # "https://fourweekmba.com/feed",
        "http://blog.eladgil.com/feeds/posts/default",
        "https://andrewchen.co/feed",
        # "https://cdixon.org/rss.xml", # Nah his stuff is really old
        # "http://gordonbrander.com/pattern.rss", # Errors out

        # HealthTech
        "https://outofpocket.health/feed"
    ]

    # Unite all feeds into one
    all_feeds = substack_feeds + custom_feeds
    return all_feeds
