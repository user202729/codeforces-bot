import time
import traceback
from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
import html

from .util import CodeforcesSubmission, wait_for_page_load

status_marker="%status" # must not contain HTML special

def set_status(driver, contest_url: str, status: str)->None:
	"""
	find the status object on the contest_url. There must be exactly one.
	example:
	status="a\na\na < b \n c ++ d & e > f <div> &#12;"
	"""
	if driver.current_url!=contest_url: driver.get(contest_url)

	assert status_marker not in status

	for _ in range(3):
		try:
			[announcement_element]=[
					announcement_element
					for announcement_element in driver.find_elements_by_css_selector("span.question-response")
					if status_marker
					in announcement_element.text
					]

			driver.execute_script(
					"arguments[0].scrollIntoView()",
					announcement_element)  # otherwise Chrome will scroll to middle of element instead
			ActionChains(driver).move_to_element(announcement_element).double_click().perform()

			ActionChains(driver).double_click(announcement_element).perform()

			view_source_code_button=driver.find_element_by_css_selector('li[role="menuitem"][title="View source code"]')
			view_source_code_button.click()

			break
		except: # suspect: very early on page load the scripts responsible for double click the announcement thing did not work
			traceback.print_exc()
			time.sleep(5)
	
			

	[response_textarea]=[element
			for element in driver.find_elements_by_css_selector(".responseText")
			if element.size["height"]!=0 and element.size["width"]!=0
			]
	driver.execute_script("arguments[0].value = arguments[1]",
			response_textarea,
			'<p><pre><code style="font-family: monospace;">' + status_marker + '\n'
			+ html.escape(status) + '</code></pre></p>'
			)

	[send_button]=[
			element
			for element in driver.find_elements_by_css_selector("div.answer-question-box input.submit[type=submit]")
			if element.size["height"]!=0 and element.size["width"]!=0
			]
	with wait_for_page_load(driver):
		send_button.click()


def get_status_url(contest_url: str)->str:
	"""
	example:
	contest_url="https://codeforces.com/group/WI3TQ5cmi9/contest/357584"
	"""

	contest_url=contest_url.rstrip("/")
	return contest_url+"/status?order=BY_ARRIVED_DESC"


def get_submissions(driver, status_url: str)->list[CodeforcesSubmission]:
	"""
	only handle first page (provided by status_url).
	"""
	driver.get(status_url)

	result=[]
	for row in driver.find_elements_by_css_selector("table.status-frame-datatable tbody tr:not(.first-row)"):
		cells=row.find_elements_by_css_selector("td")
		if len(cells)==1: continue  # special case: "No items"
		result.append(
				CodeforcesSubmission(
					problem=cells[3].find_element_by_css_selector("a").get_attribute("href").split("/")[-1],
					id=cells[0].text,
					)
				)

	return result

def build_submission_url(contest_url: str, submission_id: str)->str:
	"""
	example:
	contest_url="https://codeforces.com/group/WI3TQ5cmi9/contest/357584/"
	submission_id="137740388"
	"""
	contest_url=contest_url.rstrip("/")
	return contest_url+"/submission/"+submission_id

def get_code(driver, submission_url: str)->str:
	print("========", submission_url, driver.current_url)
	if driver.current_url!=submission_url:
		print("======== getting", submission_url)
		driver.get(submission_url)

	return driver.find_element_by_id("program-source-text").text

def do_reject(driver, submission_url: str)->None:
	if driver.current_url!=submission_url: driver.get(submission_url)

	[reject]=driver.find_elements_by_css_selector("input[value=Reject]")
	reject.click()
