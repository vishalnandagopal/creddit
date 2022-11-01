with open('config.json','r') as f:
    print(f.read())
'''
def read_and_check_config(config_error_count:int=0) -> tuple[bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,int,int,int,bool,dict,list,bool]:
    print("Reading config file")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        config_values = (
            config['run_program'], # ---------------------------------- 0
            config['cron_job_mode'], # ---------------------------------1
            config['testing_mode'], # ----------------------------------2
            config['tweet_only_link'], # -------------------------------3
            config['tweet_description'], # -----------------------------4 
            config['tweet_summarized_article'], # ----------------------5
            config['move_log_files'], # --------------------------------6
            config['delete_old_log_files'], # --------------------------7
            config['delete_important_errors'], # -----------------------8
            config['use_backup_meaning_cloud_token'], # --------------------9
            config['time_to_wait_after_tweeting_a_url_in_seconds'], #--10
            config['run_program_every_x_seconds'], # ------------------11
            config['time_to_wait_when_not_running_in_seconds'], # -----12
            config['ignore_https'], # ---------------------------------13
            config['rss_feeds_to_fetch'], # ---------------------------14
            config['dont_summarize_these_urls'], # --------------------15
            config['reset_config_to_default'], # ----------------------16
            )
    except (KeyError,FileNotFoundError,json.JSONDecodeError):
        (valid_config,config_error_count) = config_error(config_error_count)
        read_and_check_config(config_error_count)
    
    # Checks if the important properties in the config.json file are valid by seeing if their types are appropriate
    if not ( (isinstance(config['run_program'],bool)) and (isinstance(config['cron_job_mode'],bool)) and (isinstance(config['testing_mode'],bool)) and (isinstance(config['tweet_only_link'],bool)) and (isinstance(config['tweet_description'],bool)) and (isinstance(config['tweet_summarized_article'],bool)) ):
        valid_config = False
    elif not ( (isinstance(config['time_to_wait_after_tweeting_a_url_in_seconds'],int)) and (isinstance(config['run_program_every_x_seconds'],int)) ):
        valid_config = False
    elif not ( (isinstance(config['rss_feeds_to_fetch'],dict))):
        valid_config = False
    else:
        valid_config = True
    if valid_config:
        return config_values
    else:
        return None'''