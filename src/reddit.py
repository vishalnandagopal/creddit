import requests

def get_api_response(url) -> requests.Response:
    """
    Returns the json-encoded content of the api response, by requesting the given URL using the built-in requests library.
    """
    headers = {
        "User-Agent": "unofficial-reddit-terminal-app"
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/130.0"
        }
    try:
        api_response = requests.get(url,headers=headers)
        return api_response.json()
    except requests.exceptions.ConnectionError:
        print("You seem to be offline. Try connecting to a network connection.")
        import sys
        sys.exit()

def get_subreddit_dict(subreddit:str = "soccer", limit:int = 9, post_id_to_start_from:str ="") -> dict:
    """
    Constructs the api_url to load the subreddit, and loads the api_response and returns it as a dict.

    ### Parameters:
    limit = number of posts that should be present in the json response.

    post_id_to_start_from = The posts that are after this id in the feed are loaded.

    For example if you give the ID of the 9th post (eg: yjbttz) and limit=10, the posts 10,11,12 and so on till 19 are loaded.
    """
    
    if post_id_to_start_from:
        subreddit_url = f"https://api.reddit.com/r/{subreddit}?limit={limit}&after=t3_{post_id_to_start_from}"
    else:
        subreddit_url = f"https://api.reddit.com/r/{subreddit}?limit={limit}"
    
    subreddit_response = get_api_response(subreddit_url)
    return subreddit_response["data"]["children"]

def get_comments_dict(post_id:str) -> dict:
    """
    Constructs the api_url to load the comments of a post, and loads the api_response and returns it as a dict.

    ### Parameters:
    post_id = The ID of the post to load comments for yjbttz.
    """
    
    post_url = f"https://api.reddit.com/{post_id}"
    post_comments_response = get_api_response(post_url)
    return post_comments_response[1]["data"]["children"]