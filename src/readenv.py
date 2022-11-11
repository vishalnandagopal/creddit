from os import getenv, listdir
from dotenv import load_dotenv

class GlobalVariables:
    def __init__(self):
        if "reddit-terminal.env" in listdir():
            load_dotenv("reddit-terminal.env")
        else:
            load_dotenv()
        if getenv("IGNORED_USERS"):
            self.ignored_users = getenv("IGNORED_USERS").split(",")
        else:
            self.ignored_users = []
        self.posts_to_print = int(getenv("POSTS_TO_PRINT"))
        if not self.posts_to_print:
            self.posts_to_print = 10
        self.default_subreddit = getenv("DEFAULT_SUBREDDIT")
