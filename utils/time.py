from datetime import datetime

import pytz


class Time:
    @staticmethod
    async def get_current() -> datetime:
        return datetime.now(pytz.timezone("Europe/Kiev"))

    @staticmethod
    async def get_normalised() -> str:
        time = await Time.get_current()
        return time.strftime("%H:%M:%S %d.%m.%Y")
