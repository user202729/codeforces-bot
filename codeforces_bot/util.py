from typing import Any
from dataclasses import dataclass
from contextlib import contextmanager

from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support.expected_conditions import staleness_of  # type: ignore
from selenium.webdriver import Chrome  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore



@dataclass
class Submission:
	id: str
	verdict: str
	correct: bool
	running: bool


@dataclass
class CodeforcesSubmission:
	problem: str # A, B etc.
	id: str #submission id



# https://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
@contextmanager
def wait_for_page_load(driver, timeout: int=15):
	old_page = driver.find_element_by_tag_name('html')
	yield
	WebDriverWait(driver, timeout).until(staleness_of(old_page))


def start_driver(user_data_dir: str)->Any:
	options = Options()
	options.add_argument("user-data-dir=" + user_data_dir)
	driver = webdriver.Chrome(options=options)


	driver.implicitly_wait(2)
	return driver

