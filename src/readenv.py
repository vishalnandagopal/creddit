from os import getenv

from dotenv import load_dotenv


class GlobalVariables:
    """
    A class that stores all the variables that much be read from the env file. Helps me keep track of them at one place, instead of reading and using them where they are needed. This application relies on env for config.
    """

    ignored_users: list
    no_of_posts_to_print: int
    default_subreddit: str
    ignore_mod_posts: bool

    def __init__(self):
        load_dotenv()
        self.ignored_users = getenv("IGNORED_USERS", "2soccer2bot,AutoModerator").split(
            ","
        )
        self.no_of_posts_to_print = int(getenv("POSTS_TO_PRINT", "10"))
        self.default_subreddit = getenv("DEFAULT_SUBREDDIT", "soccer")
        self.ignore_mod_posts = getenv("IGNORE_MOD_POSTS", "t").casefold() in {
            "t",
            "true",
            "y",
            "yes",
        }
