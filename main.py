import requests
from colorama import Fore
# variables = variables.GlobalVariables

def get_api_response(url) -> requests.Response:
    headers = {
        "User-Agent": "unofficial-reddit-terminal-app"
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/130.0"
        }
    api_response = requests.get(url,headers=headers)
    return api_response

def take_int_input(text:str="") -> int:
    return int(input(text))

def handle_user_choice(printed_posts:dict,user_choice:int=1,type:int=0):
    if type == 0:
        post_dict = get_comments_dict(printed_posts[user_choice])
        printed_comments = print_post_comments(post_dict)

def get_subreddit_dict(subreddit:str = "soccer") -> dict:
    subreddit_url = f"https://api.reddit.com/r/{subreddit}"
    api_response = get_api_response(subreddit_url)
    subreddit_response = api_response.json()
    return subreddit_response

def get_comments_dict(post_id:str) -> dict:
    post_url = f"https://api.reddit.com/{post_id}"
    api_response = get_api_response(post_url)
    post_response = api_response.json()
    return post_response[1]

def print_subreddit_posts(subreddit_dict:dict) -> dict:
    # subrredit_dict_data is the dict subreddit_dict["data"]
    # subreddit_dict_data["children"] is a list
    count,printed_posts = 0,{}
    for entry in subreddit_dict["data"]["children"]:
        if count < 10:
            if (entry["data"]["author"] != "AutoModerator") and (entry["data"]["author"] != "2soccer2bot"):
                print(colors[count%8] + f'{count+1}. {entry["data"]["title"]}')
                print(f'    URL - {entry["data"]["url"]}' + Fore.RESET,end="\n--------------------------------------------------------------------------------------------------------------------\n")
                count += 1
                printed_posts[count+1] = entry["data"]["id"]
    print(Fore.RESET,end='')
    return printed_posts

colors = [Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

def print_post_comments(post_dict:dict) -> dict:
    # subrredit_dict_data is the dict subreddit_dict["data"]
    # subreddit_dict_data["children"] is a list
    count,printed_comments = 0,{}
    for entry in post_dict["data"]["children"]:
        if count < 10:
            if entry["data"]["author"] != "AutoModerator":
                print((colors[count%8]) + f'{count+1}. {entry["data"]["body"]}' + Fore.RESET,end="\n--------------------------------------------------------------------------------------------------------------------\n")
                count += 1
                printed_comments[count+1] = entry["data"]["id"]
    print(Fore.RESET,end='')
    return printed_comments

def job():
    subreddit = "soccer"
    sub_main_page_input_text = '''Enter the post you want to read the comments for: '''
    #subreddit = input("Enter the subreddit you want to visit: r/")
    subreddit_dict = get_subreddit_dict(subreddit)
    printed_posts = print_subreddit_posts(subreddit_dict)
    user_choice = take_int_input(sub_main_page_input_text)
    handle_user_choice(printed_posts,user_choice)
    

job()