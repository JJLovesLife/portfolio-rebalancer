from playwright.sync_api import sync_playwright
import atexit

_playwright = None
_browser = None
_page = None

def playwright_exit_handler():
	global _playwright, _browser, _page
	try:
		print("Closing Playwright...")
	except Exception as e:
		pass
	try:
		if _page is not None:
			_page.close()
		if _browser is not None:
			_browser.close()
		if _playwright is not None:
			_playwright.stop()
	except Exception as e:
		pass

def get_playwright_page():
	global _playwright, _browser, _page
	if _page is None:
		_playwright = sync_playwright().start()
		_browser = _playwright.chromium.launch(channel='chromium')
		_page = _browser.new_page()
		atexit.register(playwright_exit_handler)
	return _page
