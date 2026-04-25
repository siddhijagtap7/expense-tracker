from enum import Enum


class ExpenseScope(str, Enum):
    FAMILY = "family"
    PERSONAL = "personal"


class ExpenseType(str, Enum):
    NECESSARY = "necessary"
    UNNECESSARY = "unnecessary"


class PaymentMode(str, Enum):
    UPI = "upi"
    CASH = "cash"
    CARD = "card"
    NETBANKING = "netbanking"
    CHEQUE = "cheque"