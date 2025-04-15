class PositionCatalogueRecord:
    def __init__(self,
                 position: str = None,
                 name_uk: str = None,
                 salary: float = 0):
        self.position = position  # EmployeePosition
        self.name_uk = name_uk
        self.salary = salary
