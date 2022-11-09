from colorama import Fore
from . import reddit
import textwrap

colors_to_use_in_terminal = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.WHITE] # Fore.BLUE, Fore.MAGENTA, Fore.CYAN gives green, or purple so repetition
num_of_colors = len(colors_to_use_in_terminal)


def take_input_after_sub_print(text:str="") -> int:
    try:
        user_choice = input(text)
        return int(user_choice) if user_choice else 0
    except KeyboardInterrupt:
        print("\nExited the program")
        exit_terminal()


def exit_terminal():
    import sys
    sys.exit()


def handle_user_choice_after_a_post(printed_posts:dict, subreddit:str,start_count:int = 0):
    user_choice = take_input_after_sub_print("Enter the post you want to read the comments for, or click enter to read more posts: ")
    if user_choice:
        # Wants to read comments of a post
        print(f'{colors_to_use_in_terminal[(user_choice-1)%num_of_colors]}{printed_posts[user_choice-start_count-1][1]}{Fore.RESET}')
        print_post_comments(printed_posts[user_choice-start_count-1][0])
        handle_user_choice_after_a_post(printed_posts,subreddit,start_count)
    else:
        # Wants to read more posts from a subreddit
        last_post_id = printed_posts[-1][0]
        start_count = print_subreddit_posts(subreddit,post_id_to_start_from=last_post_id,start_count=start_count)


def print_subreddit_posts(subreddit:str,post_id_to_start_from:str="",start_count=0):
    """
    Prints the subreddit posts when you give a subreddit name
    
    subrredit_dict_data is the dict subreddit_dict["data"]
    subreddit_dict_data["children"] is a list

    #### Parameters
    subreddit = subreddit name

    post_id_to_start_from = used to connstruct the API url to ensure only the posts needed after a particular post ID are loaded 
    from the server.
    
    start_count = post number to start from in the api_response. 
    """
    subreddit_dict = reddit.get_subreddit_dict(subreddit,post_id_to_start_from=post_id_to_start_from)
    
    printed_posts = []
    # printed_posts is supposed to be of the format ["post_id","title"], where printed_posts[i-1] is the id of the i'th post printed in the terminal
    
    for entry in subreddit_dict:
        if (entry["data"]["author"] != "AutoModerator") and (entry["data"]["author"] != "2soccer2bot"):
            print(colors_to_use_in_terminal[start_count%num_of_colors] + f'{start_count+1}. {entry["data"]["title"]}')
            try:
                if entry["data"]["link_flair_richtext"][1]['t'].lower() == "official source":
                    url_source = f'    URL - {entry["data"]["url"]}\n    Official Source'
                else:
                    url_source = f'    URL - {entry["data"]["url"]}'
            except (KeyError,IndexError):
                    url_source = f'    URL - {entry["data"]["url"]}'
            print(url_source + Fore.RESET,end="\n--------------------------------------------------------------------------------------------------------------------\n")
            printed_posts.append((entry["data"]["id"],f'{entry["data"]["title"]}\n{url_source}'))
            start_count += 1
    print(Fore.RESET,end='')
    
    handle_user_choice_after_a_post(printed_posts,subreddit,start_count)


def print_post_comments(post_id: str):
    """
    Prints the subreddit posts when you give a subreddit name
    
    printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal
    
    #### Parameters
    post_id = ID of the post for which we have to load comments
    """
    post_comments_dict = reddit.get_comments_dict(post_id)
    count = 0
    for entry in post_comments_dict:
        if count < 10:
            if (entry["data"]["author"] != "AutoModerator") and (entry["data"]["author"] != "2soccer2bot"):
                prefix = '''    |
    |--- '''
                wrapper = textwrap.TextWrapper(initial_indent=prefix, width=150,subsequent_indent='    |    ')
                # Prints the comment text and it's author by giving the correct indendation to the left.
                print(wrapper.fill(entry["data"]["body"] + " --- u/" + entry["data"]["author"]))
                count += 1
        else:
            break
    print(Fore.RESET,end="\n--------------------------------------------------------------------------------------------------------------------\n")