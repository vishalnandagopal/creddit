"""
Handle all terminal functions, such as printing using different colors, taking care of user input after it, etc
"""

from html import unescape
from subprocess import Popen as background_run_command
from subprocess import run as run_command
from textwrap import TextWrapper
from typing import Any, Dict
from urllib.parse import urlparse
from webbrowser import open as web_open

from colorama import Fore

from .config import Config, check_config_existence, create_config, read_config
from .reddit import get_link_in_post, get_post_dict, get_posts_in_a_subreddit

colors_to_use_in_terminal: tuple[str, ...] = (
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.CYAN,
    Fore.MAGENTA,
)
# Fore.BLUE is very ugly in the terminal. Ineligible

num_of_colors = len(colors_to_use_in_terminal)

ending_separator = f"\n{'-' * 116}\n"

config: Config


ignored_users: list[str]
"""Posts by these users won't be printed"""


no_of_posts_to_print: int
"""The number of posts to print each time"""


ignore_all_mod_posts: bool
"""Whether to ignore mod posts. Currently not implemented"""


def introduce() -> None:
    """
    User using the app for the first time? Call this!
    """

    print(
        f"Welcome to {Fore.RED}cReddit{Fore.RESET}! Looks like you're using this app for a first time"
    )
    if input(
        f"Would you like set the config (default subreddits, ignored users, etc) [Y/n] [{Fore.GREEN}Y{Fore.RESET}]"
    ).casefold() in {"", "y"}:
        c: Dict[str, Any] = dict()

        # No of posts of print
        c["no_of_posts_to_print"] = int(
            input(f"No of posts to print in the terminal? [{Fore.GREEN}10{Fore.RESET}]")
            or 10
        )

        # Does the user want to ignore any users?
        c["ignored_users"] = input(
            f"Users you wish to ignore? (Eg: Automoderator, 2soccer2bot). Separate multiple values with a comma [{Fore.GREEN}2soccer2bot,AutoModerator{Fore.RESET}]"
        ).split(",")
        if c["ignored_users"] == [""]:
            c["ignored_users"] = ["2soccer2bot", "AutoModerator"]
        c["ignore_all_mod_posts"] = True

        # Maybe the user wants to open a subreddit by default?
        if input(
            f"Would you like to open a subreddit by default every time? [Y/n] [{Fore.GREEN}Y{Fore.RESET}]"
        ).casefold() in {"", "y"}:
            _ = input("Enter default subreddit - r/")
            while not _:
                _ = input("Enter default subreddit - r/")

            c["default_subreddit"] = _

        create_config(c)
    else:
        create_config()


def exit_terminal(error: Exception | None) -> None:
    """
    Exits the terminal and resets the terminal color to the default color:
    """

    print(Fore.RESET)
    if error:
        print(repr(error))
    exit()


def take_input_after_sub_print(text: str) -> str:
    """
    After a subreddit's post has been printed, the user's input is taken. He can give any of the 4 as input
    1. Empty input (by just entering) - Will reach more posts
    2. Post number - Will open the comments for that post
    3. Postnumber and "o" (Like "1o") to open the post in the web browser and to read the comments
    4. r/subreddit_name - Indicates he wants to stop reading this subreddit and continue to another one.

    Parameters:
        text (str): The text to print while taking input

    Returns:
        str: The input given
    """
    try:
        user_choice = input(text).casefold()
        if not user_choice:
            return ""
        if (user_choice.endswith("o")) and not user_choice[:-1].isnumeric():
            raise ValueError("Enter a valid number before the o")
        if (user_choice.startswith("r/")) and (not user_choice.isalpha()):
            raise ValueError(
                "Please enter the name of the subreddit as r/subreddit_name"
            )
        if (
            not (user_choice.endswith("o") or user_choice.startswith("r/"))
            and not user_choice.isnumeric()
        ):
            raise ValueError(
                'Please enter a valid number to read the comments, "number0" to open the link, or r/subreddit_name to read posts from a different sub'
            )
        return user_choice
    except ValueError as e:
        print(e)
        return take_input_after_sub_print(text)
    except (KeyboardInterrupt, EOFError):
        print("\nExited the program")
        exit_terminal(error=None)
    except Exception as e:
        exit_terminal(error=e)
    return ""


def handle_user_choice_after_a_post(
    printed_posts: list[str], titles: list[str], subreddit: str, start_count: int = 0
) -> None:
    """
    After a subs posts are printed, take input using another function and handle it accordingly. Open the comments, the link or another subreddit

    Parameters:
        printed_posts (list[str]): The list of all post_ids currently printed in the terminal. Used to handle input according to he number the user chooses.
        titles: (list[str]): The titles of all the posts currently printed in the terminal. Used to quickly print it before fetching comments.
        subreddit (str): To continue after the last post, in case the user wants to read more posts from the subreddit
    """
    user_choice = take_input_after_sub_print(
        """Enter the post number you want to read the comments for, or click enter to read more posts:\nTo open link and also view comments, type "o" after the number. Like "2o": """
    )
    if user_choice.endswith("o") or user_choice.isnumeric():
        if user_choice.endswith("o"):
            # Wants to open the post before reading comments

            num_choice = int(user_choice[:-1])
            open_post_link(printed_posts[num_choice - 1])
        elif user_choice.isnumeric():
            # Wants to read comments of a post

            num_choice = int(user_choice)
            if num_choice > len(printed_posts) or num_choice < 1:
                print(
                    f"{Fore.RED}Number must be >= 1 and <= {len(printed_posts)}{Fore.RESET}"
                )
                return handle_user_choice_after_a_post(
                    printed_posts, titles, subreddit, start_count
                )

        # Colored post title
        post_title = f"{colors_to_use_in_terminal[(num_choice - 1) % num_of_colors]}{titles[num_choice - 1]}{Fore.RESET}"
        print(post_title)

        print_post_comments(printed_posts[num_choice - 1])
        handle_user_choice_after_a_post(printed_posts, titles, subreddit, start_count)
    else:
        # Wants to read more posts from the same subreddit
        last_post_id = printed_posts[-1]
        print_subreddit_posts(
            subreddit, post_id_to_start_from=last_post_id, start_count=start_count
        )


def print_subreddit_posts(
    subreddit: str,
    post_id_to_start_from: str | None = None,
    start_count: int = 0,
) -> None:
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
        limit=(no_of_posts_to_print),
        after_post=post_id_to_start_from,
    )

    printed_posts: list[str] = list()
    titles: list[str] = list()
    # printed_posts is supposed to be of the format ["post_id",...], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    print(f"r/{subreddit}", end="\n\n")
    for entry in subreddit_dict:
        if entry["data"]["author"] not in ignored_users:
            print_post_body(entry, start_count)
            printed_posts.append(entry["data"]["id"])
            titles.append(entry["data"]["title"])
            start_count += 1

    print(Fore.RESET, end="")

    handle_user_choice_after_a_post(printed_posts, titles, subreddit, start_count)


def print_post_body(specific_entry: dict[str, dict], start_count: int) -> None:
    """
    Called from `print_subreddit_posts()`, this functions handles the printing of a body content for a post.

    Parameters:
    specific_entry dict[str,dict]: Dict containing details of a comments, fetched using the Reddit API.
    """

    print(
        colors_to_use_in_terminal[start_count % num_of_colors]
        + f"{start_count + 1}. {unescape(specific_entry['data']['title'])}"
    )
    try:
        if (
            specific_entry["data"]["link_flair_richtext"][1]["t"].lower()
            == "official source"
        ):
            post_url_source = (
                f"    URL - {specific_entry['data']['url']}\n    Official Source"
            )
        else:
            post_url_source = f"    URL - {specific_entry['data']['url']}"
    except (KeyError, IndexError):
        post_url_source = f"    URL - {specific_entry['data']['url']}"
    print(
        f"{post_url_source}{Fore.RESET}",
        end=ending_separator,
    )


def print_comment(specific_comment_entry: dict) -> None:
    """
    Called from `print_post_comments()`, this functions handles the printing for a specific comment

    Parameters:
    specific_entry (str): Dict containing details of a comments, fetched using the Reddit API.
    """

    prefix = """    |
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


def print_post_comments(post_id: str) -> None:
    """
    Prints the subreddit posts when you give a subreddit name

    printed_posts is supposed to be of the format ["post_id"], where printed_posts[i-1] is the id of the i'th post printed in the terminal

    Parameters:
        post_id (str): ID of the post for which we have to load comments.
        post_title (str): The title of the post to print before printing out the comments
    """

    post_comments_dict = get_post_dict(post_id)[1]["data"]["children"]
    count = 0

    for entry in post_comments_dict:
        if count < 10:
            if entry["data"]["author"] not in ignored_users:
                print_comment(entry["data"])
                count += 1
        else:
            break

    print(Fore.RESET, end=ending_separator)


def open_post_link(post_id: str) -> None:
    """
    When the link mentioned in a post is passed to this, it tries to determine if it is a video that can be opened in MPV. If possible, it opens it directly in MPV. Else, for other links, it opens it in the defauly web browser using the `webbrowser` module.

    Parameters:
        post_id (str):
    """

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


def cls() -> None:
    """This somehow clears the screen. https://stackoverflow.com/a/50560686"""
    print("\033[H\033[J", end="")


def run() -> None:
    """
    Callable function to be used while running from the terminal
    """
    global \
        config, \
        ignored_users, \
        no_of_posts_to_print, \
        ignore_all_mod_posts, \
        default_subreddit

    # Clear screen
    cls()

    if not check_config_existence():
        introduce()

    config = read_config()

    ignored_users = config["ignored_users"]

    no_of_posts_to_print = int(config["no_of_posts_to_print"])
    subreddit = (
        str(config["default_subreddit"])
        if "default_subreddit" in config
        else input("Enter the subreddit you want to visit: r/")
    )

    ignore_all_mod_posts = bool(config["ignore_all_mod_posts"])

    if not subreddit:
        print("No subreddit entered.")
        exit_terminal(error=None)
    print_subreddit_posts(subreddit)
