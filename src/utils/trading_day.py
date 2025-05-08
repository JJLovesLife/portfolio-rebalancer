from datetime import date, datetime, timedelta
from pytz import timezone

holidays = {
	2025: [(1, 1), (1, 28), (1, 29), (1, 30), (1, 31), (2, 3), (2, 4), (4, 4), (5, 1), (5, 2), (5, 5), (6, 2), (10, 1), (10, 2), (10, 3), (10, 6), (10, 7), (10, 8)]
}

us_holidays = {
	2025: [(1, 1), (1, 9), (1, 20), (2, 17), (4, 18), (5, 26), (6, 19), (7, 4), (9, 1), (11, 27), (12, 25)]
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
