from html import unescape
from random import random
from sys import stdout
from textwrap import TextWrapper
from time import sleep

from colorama import Fore

from . import readenv, reddit

colors_to_use_in_terminal = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN]
# Fore.BLUE, Fore.MAGENTA, Fore.CYAN gives green, or purple, etc. So repetition

num_of_colors = len(colors_to_use_in_terminal)

ending_separator = "\n" + "-" * 116 + "\n"


# global_variables
global_variables = readenv.GlobalVariables()


def handle_main(subreddit: str):
    print_subreddit_posts(subreddit)


def exit_terminal(error: Exception, exit: bool = True) -> None:
    """
    Exits the terminal and resets the terminal color to the default color:
    """
    import sys

    print(Fore.RESET)
    if error:
        print(repr(error))
    if exit:
        sys.exit()


def take_input_after_sub_print(text: str = "") -> int:
    try:
        user_choice = input(text)
        try:
            return int(user_choice) if user_choice else 0
        except ValueError:
            print("Invalid input, enter again")
            take_input_after_sub_print(text)
    except (KeyboardInterrupt, EOFError):
        print("\nExited the program")
        exit_terminal(error=None)
    except Exception as e:
        exit_terminal(error=e)


def slow_print(to_print: str) -> bool:
    for letter in to_print:
        sleep(random() / 100)
        stdout.write(letter)
        stdout.flush()
    print("")
    return True


def handle_user_choice_after_a_post(
    printed_posts: dict, subreddit: str, start_count: int = 0
):
    user_choice = take_input_after_sub_print(
        "Enter the post you want to read the comments for, or click enter to read more posts: "
    )
    if user_choice:
        # Wants to read comments of a post
        post_title = f"{colors_to_use_in_terminal[(user_choice-1)%num_of_colors]}{printed_posts[user_choice-1][1]}{Fore.RESET}"
        print_post_comments(printed_posts[user_choice - 1][0], post_title)
        handle_user_choice_after_a_post(printed_posts, subreddit, start_count)
    else:
        # Wants to read more posts from a subreddit
        last_post_id = printed_posts[-1][0]
        start_count = print_subreddit_posts(
            subreddit, post_id_to_start_from=last_post_id, start_count=start_count
        )


def print_post_body(specific_entry: dict[str], start_count: int) -> str:
    """
    Called from `print_subreddit_posts()`, this functions handles the printing of a body content for a post.

    Parameters:
        specific_entry
            Dict containing details of a comments, fetched using the Reddit API.
    """

    print(
        colors_to_use_in_terminal[start_count % num_of_colors]
        + f'{start_count+1}. {unescape(specific_entry["data"]["title"])}'
    )
    try:
        if (
            specific_entry["data"]["link_flair_richtext"][1]["t"].lower()
            == "official source"
        ):
            post_url_source = (
                f'    URL - {specific_entry["data"]["url"]}\n    Official Source'
            )
        else:
            post_url_source = f'    URL - {specific_entry["data"]["url"]}'
    except (KeyError, IndexError):
        post_url_source = f'    URL - {specific_entry["data"]["url"]}'
    print(
        post_url_source + Fore.RESET,
        end=ending_separator,
    )
    return post_url_source


def print_subreddit_posts(
    subreddit: str,
    post_id_to_start_from: str = "",
    start_count: int = 0,
    printed_posts: list = [],
):
    """
    Prints the subreddit posts when you give a subreddit name

    subrredit_dict_data is the dict subreddit_dict["data"], and subreddit_dict_data["children"] is a list.

    Parameters
        subreddit
            Name of the subreddit.
        post_id_to_start_from
            Used to connstruct the API url to ensure only the posts needed after a particular post ID are loaded from the server.
        start_count
            Post number to start from in the api_response.
    """

    reddit.get_subreddit_dict(subreddit)
    subreddit_dict = reddit.get_subreddit_dict(
        subreddit,
        limit=(global_variables.posts_to_print - 1),
        post_id_to_start_from=post_id_to_start_from,
    )
    # printed_posts is supposed to be of the format ["post_id","title"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    for entry in subreddit_dict:
        if entry["data"]["author"] not in global_variables.ignored_users:
            post_url_source = print_post_body(entry, start_count)
            printed_posts.append(
                (entry["data"]["id"], f'{entry["data"]["title"]}\n{post_url_source}')
            )
            start_count += 1
    print(Fore.RESET, end="")
    handle_user_choice_after_a_post(printed_posts, subreddit, start_count)


def print_comment(specific_comment_entry: dict[str]):
    """
    Called from `print_post_comments()`, this functions handles the printing for a specific comment

    Parameters:
        specific_entry
            Dict containing details of a comments, fetched using the Reddit API.
    """

    prefix = f"""    |
    |--- """
    wrapper = TextWrapper(
        initial_indent=prefix, width=150, subsequent_indent="    |    "
    )
    # Prints the comment text and it's author by giving the correct indendation to the left.
    print(
        wrapper.fill(
            unescape(specific_comment_entry["body"])
            + " --- u/"
            + unescape(specific_comment_entry["author"])
        )
    )


def print_post_comments(post_id: str, post_title: str):
    """
    Prints the subreddit posts when you give a subreddit name

    printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    Parameters:
        post_id
            ID of the post for which we have to load comments.
        post_title
            The title of the post to print before printing out the comments
    """

    slow_print(post_title)
    get_comments_task = reddit.get_comments_dict(post_id)
    post_details = get_comments_task
    post_comments_dict = post_details[1]
    if post_details[0]:
        print(unescape(post_details[0]))
    count = 0
    for entry in post_comments_dict:
        if count < 10:
            if entry["data"]["author"] not in global_variables.ignored_users:
                print_comment(entry["data"])
                count += 1
        else:
            break
    print(Fore.RESET, end=ending_separator)
