"""
Manage API connections with and responses from Reddit
"""

from functools import lru_cache

from requests import get as r_get
from requests.exceptions import ConnectionError


@lru_cache(maxsize=None)
def get_api_response(url: str) -> dict:
    """
    Returns the json-encoded content of the api response, by requesting the given URL using the built-in requests library.
    Parameters:
        url (str):URL to load using requests library

    Returns:
        requests.Response
    """

    # Caching the resposes for every URL, since I might be calling it again and again for posts/comments, etc, and the response doesn't really change in a few minutes. When the application is run next (after a few hours, days, weeks), it would be running as a fresh instance and the response would be fetched again.

    headers = {
        "User-Agent": "cli:reddit-cli:v1.0.0 (by /u/vishalnandagopal)"
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/130.0"
    }
    try:
        api_response = r_get(url=url, headers=headers)
        if api_response.status_code != 200:
            raise RuntimeError(f"Error with API - \n{api_response}")
        return api_response.json()
    except ConnectionError:
        raise ConnectionError("You seem to be offline. Try connecting to a network.")


def get_posts_in_a_subreddit(
    subreddit: str, limit: int = 10, after_post: str | None = None
) -> list[dict]:
    """
    Constructs the api_url to load the subreddit, and loads the api_response and returns it as a dict.

    Parameters:
        limit (int):number of posts that should be present in the json response.

        after_post (int):The posts that are after this id in the feed are loaded.

    For example if you give the ID of the 9th post (eg: yjbttz) and limit=10, the posts 10,11,12 and so on till 19 are loaded.

    Returns
    Dict: Subreddit response as key value pair of index and post_details.
    """

    subreddit_url = f"https://api.reddit.com/r/{subreddit}?limit={limit}"

    if after_post:
        subreddit_url += f"&after=t3_{after_post}"

    subreddit_response = get_api_response(subreddit_url)
    return subreddit_response["data"]["children"]


def get_post_dict(post_id) -> dict:
    """
    Constructs the api_url to load the comments of a post, and loads the api_response and returns it as a tuple, with the first element being the post text, and the second element being a dict of the comments.

    Parameters:
        post_id (str):The ID of the post to load comments for. Eg: yjbttz.

    Returns:
        dict: The JSON response of the API, parsed as a dict
    """

    # LRU caching this function doesn't really help, since it only calls the API and returns it. The API function is already cached using the same lru_cache decorator.
    post_url = f"https://api.reddit.com/{post_id}"
    return get_api_response(post_url)


def get_post_text(post_id: str) -> str:
    """
    Fetches the text of the post, if any

    Parameters:
        post_id (str): The post ID

    Returns:
        str: The text of the post
    """
    try:
        return get_post_dict(post_id)[0]["data"]["children"][0]["data"]["selftext"]
    except KeyError:
        return ""


def get_comments_dict(post_id: str) -> dict[int, dict]:
    """
    Fetches the dict for the post and returns only a tuple of the text in the post (if any), and the a dict of the comments. the api_url to load the comments of a post, and loads the api_response and returns it as a tuple, with the first element being the post text, and the second element being a dict of the comments.

    Parameters:
        post_id (str):The ID of the post to load comments for. Eg: yjbttz.

    Returns:
        dict: The comments dict. Key value pair of int and each comment's dict
    """
    post_comments_response = get_post_dict(post_id)
    return post_comments_response[1]["data"]["children"]


def get_link_in_post(post_id: str) -> str:
    """
    Fetches the link in the post. If it is a reddit video, it sends the fallback URL so that it links directly to the video. Reddit redirects video links to the post page, which is unecessary

    Parameters:
        post_id (str): The ID of the post to fetch the posted link

    Returns:
        str: The link
    """
    _ = get_post_dict(post_id)[0]["data"]["children"][0]["data"]
    if _["is_video"]:
        return _["media"]["reddit_video"]["fallback_url"]
    else:
        return _["url"]
