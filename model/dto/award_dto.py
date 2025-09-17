from dataclasses import dataclass

from model.database.awards import Award


@dataclass
class AwardDTO:
    award: Award
    issue_date: str
