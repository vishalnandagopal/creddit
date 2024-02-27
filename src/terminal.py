from html import unescape
from random import random
from subprocess import run as run_command, Popen as background_run_command
from sys import stdout
from textwrap import TextWrapper
from time import sleep
from urllib.parse import urlparse
from webbrowser import open as web_open

from colorama import Fore

from .readenv import GlobalVariables
from .reddit import get_link_in_post, get_post_dict, get_posts_in_a_subreddit

env = GlobalVariables()

colors_to_use_in_terminal = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN]
# Fore.BLUE, Fore.MAGENTA, Fore.CYAN gives green, or purple, etc. So repetition

num_of_colors = len(colors_to_use_in_terminal)

ending_separator = f"\n{'-' * 116}\n"


def exit_terminal(error: Exception | None) -> None:
    """
    Exits the terminal and resets the terminal color to the default color:
    """

    print(Fore.RESET)
    if error:
        print(repr(error))
    exit()


def take_input_after_sub_print(text: str = "") -> str:
    try:
        user_choice = input(text)
        if not user_choice:
            return ""
        if (user_choice.casefold().endswith("o")) and not user_choice[:-1].isnumeric():
            raise ValueError("Enter a valid number before 0")
        if (not user_choice.casefold().endswith("o")) and (not user_choice.isnumeric()):
            raise ValueError(
                'Please enter a valid number, or "number0" to open the link.'
            )
        return user_choice.casefold()
    except ValueError as e:
        print(e)
        return take_input_after_sub_print(text)
    except (KeyboardInterrupt, EOFError):
        print("\nExited the program")
        exit_terminal(error=None)
    except Exception as e:
        exit_terminal(error=e)
    return ""


def slow_print(to_print: str) -> bool:
    for letter in to_print:
        sleep(random() / 100)
        stdout.write(letter)
        stdout.flush()
    print("")
    return True


def print_subreddit_posts(
    subreddit: str,
    post_id_to_start_from: str | None = None,
    start_count: int = 0,
):
    """
    Prints the subreddit posts when you give a subreddit name

    subrredit_dict_data is the dict subreddit_dict["data"], and subreddit_dict_data["children"] is a list.

    Parameters:
        subreddit (str): Name of the subreddit.
        post_id_to_start_from (str) : Used to connstruct the API url to ensure only the posts needed after a particular post ID are loaded from the server.
        start_count (int) : Post number to start from in the api_response.
    """

    subreddit_dict = get_posts_in_a_subreddit(
        subreddit,
        limit=(env.no_of_posts_to_print),
        after_post=post_id_to_start_from,
    )

    printed_posts: list[str] = list()
    titles: list[str] = list()
    # printed_posts is supposed to be of the format ["post_id",...], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    print(f"r/{subreddit}", end="\n\n")
    for entry in subreddit_dict:
        if entry["data"]["author"] not in env.ignored_users:

            print_post_body(entry, start_count)
            printed_posts.append(entry["data"]["id"])
            titles.append(entry["data"]["title"])
            start_count += 1
    print(Fore.RESET, end="")
    handle_user_choice_after_a_post(printed_posts, titles, subreddit, start_count)


def handle_user_choice_after_a_post(
    printed_posts: list[str], titles: list[str], subreddit: str, start_count: int = 0
):
    user_choice = take_input_after_sub_print(
        f"""Enter the post number you want to read the comments for, or click enter to read more posts:\nTo open link and also view comments, type "o" after the number. Like "2o": """
    )
    if user_choice.endswith("o") or user_choice.isnumeric():

        if user_choice.endswith("o"):
            # Wants to open the post before reading comments

            num_choice = int(user_choice[:-1])
            open_post_link(printed_posts[num_choice - 1])
        else:
            # Wants to read comments of a post

            num_choice = int(user_choice)

        # Colored post title
        post_title = f"{colors_to_use_in_terminal[(num_choice-1)%num_of_colors]}{titles[num_choice - 1]}{Fore.RESET}"
        print(post_title)  # slow_print(post_title)

        print_post_comments(printed_posts[num_choice - 1])
        handle_user_choice_after_a_post(printed_posts, titles, subreddit, start_count)
    else:
        # Wants to read more posts from the same subreddit
        last_post_id = printed_posts[-1]
        print_subreddit_posts(
            subreddit, post_id_to_start_from=last_post_id, start_count=start_count
        )


def print_post_body(specific_entry: dict[str, dict], start_count: int) -> None:
    """
    Called from `print_subreddit_posts()`, this functions handles the printing of a body content for a post.

    Parameters:
    specific_entry dict[str,dict]: Dict containing details of a comments, fetched using the Reddit API.
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


def print_comment(specific_comment_entry: dict):
    """
    Called from `print_post_comments()`, this functions handles the printing for a specific comment

    Parameters:
    specific_entry (str): Dict containing details of a comments, fetched using the Reddit API.
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


def print_post_comments(post_id: str):
    """
    Prints the subreddit posts when you give a subreddit name

    printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    Parameters:
    post_id (str): ID of the post for which we have to load comments.
    post_title (str): The title of the post to print before printing out the comments
    """
    post_comments_dict = get_post_dict(post_id)[1]["data"]["children"]
    # if post_details[0]:
    #     print(unescape(post_details[0]))
    count = 0
    for entry in post_comments_dict:
        if count < 10:
            if entry["data"]["author"] not in env.ignored_users:
                print_comment(entry["data"])
                count += 1
        else:
            break
    print(Fore.RESET, end=ending_separator)


# async def arun_command(cmd):
#     proc = await asyncio.create_subprocess_shell(
#         cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
#     )

#     stdout, stderr = await proc.communicate()

#     print(f"[{cmd!r} exited with {proc.returncode}]")
#     if stdout:
#         print(f"[stdout]\n{stdout.decode()}")
#     if stderr:
#         print(f"[stderr]\n{stderr.decode()}")


def open_post_link(post_id: str) -> None:

    link = get_link_in_post(post_id)
    domain = str(urlparse(link).netloc)
    if domain.casefold() in {
        "v.redd.it",
    }:
        if run_command(["mpv", "--version"]):
            print("Opening it in MPV")
            # Open the video using MPV in a loop
            background_run_command(["mpv", link, "--loop"])
        else:
            print("Opening in browser")
            web_open(link)
    else:
        web_open(link)
