class Artifact:
    def __init__(self,
                 artifact_id: int = 0,
                 owner_id: int = 0,
                 name: str = None,
                 description: str = None):
        self.artifact_id = artifact_id
        self.owner_id = owner_id
        self.name = name
        self.description = description

    # Getters
    def get_artifact_id(self):
        return self.artifact_id

    def get_owner_id(self):
        return self.owner_id

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    # Setters
    def set_artifact_id(self, artifact_id):
        self.artifact_id = artifact_id

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description
