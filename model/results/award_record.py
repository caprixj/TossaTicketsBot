from dataclasses import dataclass

from model.database.award import Award


@dataclass
class AwardRecord:
    award: Award
    issue_date: str
