import os
import time
import traceback
import subprocess
from typing import Optional
import tempfile

try: from .util import Submission
except ImportError: assert Submission #iPython somehow
	
def is_logged_in(driver)->bool:
	try:
		return bool(driver.find_elements_by_css_selector("form[action*=logout]"))
	except:
		traceback.print_exc()
		return False


def wait_for_login(driver)->None:
	while not is_logged_in(driver):
		print("Waiting for log in...")
		time.sleep(5)


def get_submissions(driver, url: str)->list[Submission]:
	if driver.current_url!=url: driver.get(url)
	# because fortunately Yandex automatically reload

	wait_for_login(driver)

	if driver.current_url!=url: driver.get(url)

	if driver.current_url!=url: assert False

	from selenium.common.exceptions import StaleElementReferenceException  # type: ignore
	while True:
		try:
			result: list[Submission]=[]
			for row in driver.find_elements_by_css_selector("table.table_role_submits tbody tr.table__row"):
				verdict=row.find_elements_by_css_selector("td")[4].text
				result.append(Submission(
					id=row.find_elements_by_css_selector("td")[1].text,
					verdict=verdict,
					correct=(verdict=="OK"),
					running=(verdict=="Running"),
					))
			return result
		except StaleElementReferenceException:
			traceback.print_exc()


# IMPORTANT! Do not support multithreading / multiple processes submit at same time
def do_submit(driver, url: str, code: str, suffix: str=".cpp")->Submission:

	with tempfile.NamedTemporaryFile(
			mode="w",
			prefix="code", suffix=suffix, delete=False
			) as f:
		print(f.name)
		f.write(
				f"// time-limit: 1000\n"
				f"// problem-url: {url}\n"
				+ code)
		f.close()

		try:
			for _ in range(100):
				try:
					subprocess.run(
							["/bin/cpb",
								"submit",
								f.name], check=True)

					break
				except:
					traceback.print_exc()
					time.sleep(10)

		finally:
			os.unlink(f.name)

	new_submissions=get_submissions(driver, url)
	return new_submissions[0]  # by Yandex order~
