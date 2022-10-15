from colorama import Fore
import src.reddit as reddit
import textwrap

colors_to_use_in_terminal = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.WHITE] # Fore.BLUE, Fore.MAGENTA, Fore.CYAN gives green, or purple so repetition

def take_input_after_sub_print(text:str="") -> int:
    user_choice = input(text)
    return int(user_choice) if user_choice else 0

def handle_user_choice(printed_posts:dict,user_choice:int=1):
    if user_choice:
        #Wants to read comments of a post
        print(f'{colors_to_use_in_terminal[(user_choice-1)%7]}{printed_posts[user_choice-1][1]}{Fore.RESET}')
        post_comments_dict = reddit.get_comments_dict(printed_posts[user_choice-1][0])
        print_post_comments(post_comments_dict)
    else:
        return 0

def print_subreddit_posts(subreddit_dict:dict) -> list:
    # subrredit_dict_data is the dict subreddit_dict["data"]
    # subreddit_dict_data["children"] is a list
    printed_posts = []
    count = 0
    # printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    for entry in subreddit_dict["data"]["children"]:
        if count < 10:
            if (entry["data"]["author"] != "AutoModerator") and (entry["data"]["author"] != "2soccer2bot"):
                print(colors_to_use_in_terminal[count%len(colors_to_use_in_terminal)] + f'{count+1}. {entry["data"]["title"]}')
                try:
                    if entry["data"]["link_flair_richtext"][1]['t'].lower() == "official source":
                        url_source = f'    URL - {entry["data"]["url"]}\n    Official Source'
                    else:
                        url_source = f'    URL - {entry["data"]["url"]}'
                except (KeyError,IndexError):
                        url_source = f'    URL - {entry["data"]["url"]}'
                print(url_source + Fore.RESET,end="\n--------------------------------------------------------------------------------------------------------------------\n")
                printed_posts.append((entry["data"]["id"],f'{entry["data"]["title"]}\n{url_source}'))
                count += 1
        else:
            break
    print(Fore.RESET,end='')
    return printed_posts

def print_post_comments(post_comments_dict: dict):
    count = 0
    # printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    for entry in post_comments_dict["data"]["children"]:
        if count < 10:
            if (entry["data"]["author"] != "AutoModerator") and (entry["data"]["author"] != "2soccer2bot"):
                prefix = '''    |
    |--- '''
                wrapper = textwrap.TextWrapper(initial_indent=prefix, width=150,subsequent_indent='    |    ')
                print(wrapper.fill(entry["data"]["body"]))
                count += 1
        else:
            break
    print(Fore.RESET,end='')