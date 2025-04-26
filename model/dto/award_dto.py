from dataclasses import dataclass

from model.database import Award


@dataclass
class AwardDTO:
    award: Award
    issue_date: str
