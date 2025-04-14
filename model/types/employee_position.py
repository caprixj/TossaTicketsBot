from enum import Enum


class EmployeePosition(str, Enum):
    none = 'none'
    alliance_deputy = 'al-dep'
    independent_deputy = 'indi-dep'
    president = 'pres'
    collegium_member = 'col-member'
    collegium_chairman = 'col-chairman'
