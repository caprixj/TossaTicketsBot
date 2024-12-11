class RunModeSettings:
    def __init__(self,
                 bot_token: str = None,
                 group_chat_id: int = 0,
                 db_file_path: str = None):
        self.bot_token = bot_token
        self.group_chat_id = group_chat_id
        self.db_file_path = db_file_path

    def __repr__(self):
        return (f"RunModeSettings(bot_token={self.bot_token}, "
                f"group_chat_id={self.group_chat_id}, "
                f"db_file_path={self.db_file_path})")
