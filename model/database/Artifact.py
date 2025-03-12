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
