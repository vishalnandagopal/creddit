import requests

def get_api_response(url) -> requests.Response:
    headers = {
        "User-Agent": "unofficial-reddit-terminal-app"
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/130.0"
        }
    try:
        api_response = requests.get(url,headers=headers)
        return api_response
    except requests.exceptions.ConnectionError:
        print("You seem to be offline. Try connecting to a network connection.")
        import sys
        sys.exit()

def get_subreddit_dict(subreddit:str = "soccer") -> dict:
    subreddit_url = f"https://api.reddit.com/r/{subreddit}"
    api_response = get_api_response(subreddit_url)
    subreddit_response = api_response.json()
    return subreddit_response

def get_comments_dict(post_id:str) -> dict:
    post_url = f"https://api.reddit.com/{post_id}"
    api_response = get_api_response(post_url)
    post_comments_response = api_response.json()
    return post_comments_response[1]