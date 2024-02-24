from datetime import datetime


class TimeConfig:
    DATETIME = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    DATE = datetime.now().strftime("%Y-%m-%d")
    TIME = datetime.now().strftime("%H:%M:%S")
