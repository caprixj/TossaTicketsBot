import copy


class Member:
    def __init__(self,
                 user_id: int = 0,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 tickets_count: int = 0):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.tickets_count = tickets_count

    # Getters
    def get_id(self):
        return self.user_id

    def get_username(self):
        return self.username

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_tickets_count(self):
        return self.tickets_count

    def get_artifacts(self):
        pass

    # Setters
    def set_id(self, user_id):
        self.user_id = user_id

    def set_username(self, username):
        self.username = username

    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_tickets_count(self, tickets_count):
        self.tickets_count = tickets_count

    def set_artifact(self, artifact):
        pass
