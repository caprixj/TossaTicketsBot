from typing import Dict, Optional, Any

from aiogram.types import Message

from command.parser.core.overload import CommandOverload


class CommandParserResult:
    def __init__(self,
                 valid: bool = False,
                 message: Message = None,
                 overload: Optional[CommandOverload] = None,
                 args: Optional[Dict[str, Any]] = None,
                 creator_violation: bool = False,
                 private_violation: bool = False,
                 public_violation: bool = False):
        self.valid = valid
        self.message = message
        self.overload = overload
        self.args = args
        self.creator_violation = creator_violation
        self.private_violation = private_violation
        self.public_violation = public_violation
