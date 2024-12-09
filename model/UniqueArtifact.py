from dataclasses import dataclass
from typing import Optional


@dataclass
class UniqueArtifact:
    name: str

    id: Optional[int] = None
    description: Optional[str] = None

