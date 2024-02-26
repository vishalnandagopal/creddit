from src.terminal import env, exit_terminal, print_subreddit_posts


if env.default_subreddit:
    subreddit = env.default_subreddit
else:
    subreddit = input("Enter the subreddit you want to visit: r/")
    if not subreddit:
        print("No subreddit entered.")
        exit_terminal(error=None)

if __name__ == "__main__":
    print_subreddit_posts(subreddit)
