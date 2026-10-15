import os

WAITER_PIN = os.getenv("WAITER_PIN", "")
CONFIRMATION_TTL_MINUTES = int(os.getenv("CONFIRMATION_TTL_MINUTES", "15"))
