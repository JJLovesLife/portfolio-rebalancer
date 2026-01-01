from datetime import date, datetime, timedelta
from pytz import timezone

def gen_holidays(year: int, calendar_name: str = "NYSE"):
	import pandas as pd
	import pandas_market_calendars as mcal
	schedule = mcal.get_calendar(calendar_name).schedule(start_date=f"{year}-01-01", end_date=f"{year}-12-31")
	all_weekdays = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq="B")
	return [(d.date().month, d.date().day) for d in all_weekdays if d.date() not in set(schedule.index.date)]

holidays = {
	2025: [(1, 1), (1, 28), (1, 29), (1, 30), (1, 31), (2, 3), (2, 4), (4, 4), (5, 1), (5, 2), (5, 5), (6, 2), (10, 1), (10, 2), (10, 3), (10, 6), (10, 7), (10, 8)],
	2026: [(1, 1), (1, 2), (2, 16), (2, 17), (2, 18), (2, 19), (2, 20), (2, 23), (4, 6), (5, 1), (5, 4), (5, 5), (6, 19), (9, 25), (10, 1), (10, 2), (10, 5), (10, 6), (10, 7)]
}

us_holidays = {
	2025: [(1, 1), (1, 9), (1, 20), (2, 17), (4, 18), (5, 26), (6, 19), (7, 4), (9, 1), (11, 27), (12, 25)],
	2026: [(1, 1), (1, 19), (2, 16), (4, 3), (5, 25), (6, 19), (7, 3), (9, 7), (11, 26), (12, 25)]
}

def get_previous_trading_day(date: date, include_given_day: bool = False, us: bool = False) -> date:
	trade_date = date - timedelta(days=1) if not include_given_day else date
	year_holidays = (holidays if not us else us_holidays).get(trade_date.year, None)
	if year_holidays is None:
		raise ValueError(f"Year {trade_date.year} not provided in holidays, please add it to the holidays dictionary.")
	while True:
		if trade_date.weekday() < 5 and (trade_date.month, trade_date.day) not in year_holidays:
			return trade_date
		trade_date -= timedelta(days=1)

def get_next_trading_day(date: date, include_given_day: bool = False, us: bool = False) -> date:
	trade_date = date + timedelta(days=1) if not include_given_day else date
	year_holidays = (holidays if not us else us_holidays).get(trade_date.year, None)
	if year_holidays is None:
		raise ValueError(f"Year {trade_date.year} not provided in holidays, please add it to the holidays dictionary.")
	while True:
		if trade_date.weekday() < 5 and (trade_date.month, trade_date.day) not in year_holidays:
			return trade_date
		trade_date += timedelta(days=1)

def is_trading_day(date: date, us: bool = False) -> bool:
	year_holidays = (holidays if not us else us_holidays).get(date.year, None)
	if year_holidays is None:
		raise ValueError(f"Year {date.year} not provided in holidays, please add it to the holidays dictionary.")
	return date.weekday() < 5 and (date.month, date.day) not in year_holidays

latest_china_trading_day = get_previous_trading_day((datetime.now() + timedelta(hours=-15)).date(), True, False)
latest_us_trading_day = get_previous_trading_day((datetime.now(timezone('US/Eastern')) + timedelta(hours=-16)).date(), True, True)
