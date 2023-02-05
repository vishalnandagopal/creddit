import src.terminal as terminal

def job(subreddit: str = "soccer"):
    terminal.handle_main(subreddit)


if terminal.global_variables.default_subreddit:
    subreddit = terminal.global_variables.default_subreddit
else:
    subreddit = input("Enter the subreddit you want to visit: r/")
    if not subreddit:
        print("No subreddit entered.")
        terminal.exit_terminal()

if __name__ == "__main__":
    job(subreddit)
# except Exception as e:
# terminal.exit_terminal(error=e,exit=False)
