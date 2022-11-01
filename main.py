import src.terminal as terminal

def job(subreddit:str="soccer"):
    terminal.print_subreddit_posts(subreddit)

subreddit = input("Enter the subreddit you want to visit: r/")
job(subreddit)