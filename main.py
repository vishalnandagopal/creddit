import src.reddit as reddit, src.read_config as configuration, src.terminal as terminal

def job(subreddit:str="soccer"):
    subreddit_dict = reddit.get_subreddit_dict(subreddit)
    printed_posts = terminal.print_subreddit_posts(subreddit_dict)
    
    user_choice = terminal.take_input_after_sub_print("Enter the post you want to read the comments for, or click enter to read more posts: ")
    terminal.handle_user_choice(printed_posts,user_choice)

subreddit = input("Enter the subreddit you want to visit: r/")
job(subreddit)