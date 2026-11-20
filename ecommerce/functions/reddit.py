"""Gets posts from Reddit's JSON feed."""
import requests


def get_reddit_posts(subreddit="django"):
    """Get the newest posts from a subreddit.

    Gives back a list of posts with the title, author and url, or None if
    something went wrong.
    """
    # make the URL for the subreddit's JSON feed
    url = f"https://www.reddit.com/r/{subreddit}/.json"
    # Reddit blocks requests that don't have a User-Agent
    headers = {"User-Agent": "DjangoEcommerceApp/1.0"}

    # send the request (timeout so the page doesn't load forever)
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException:
        print("Couldn't connect to Reddit.")
        return None

    # if Reddit sends back an error
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None

    # turn the JSON into a dictionary
    data = response.json()
    posts = []

    # get the title, author and link from each post
    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "title": post["title"],
            "author": post["author"],
            # permalink is the link to the post on Reddit
            "url": "https://www.reddit.com" + post["permalink"],
        })

    return posts
