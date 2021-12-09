#!/bin/python
from typing import Any
import traceback
import time
from typing import Dict

from . import codeforces, yandex, util


def main()->None:
	import argparse
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--user-data-dir", help="Chrome user data directory.", required=True)
	parser.add_argument("--max-ignore", help="Maximum (inclusive) Codeforces id value to ignore", type=int, default=0)
	parser.add_argument("--wait-initial", action="store", default=0, type=int,
			help="Wait before start (seconds).")
	parser.add_argument("contest", help="Codeforces contest URL")
	parser.add_argument("-m", "--map", nargs=2, help="Example: --map A https://yandex.com/problem/A. Can be specified multiple times", action="append")

	# testing/developer arguments
	parser.add_argument("--test-set-status", type=str, default=None)

	args=parser.parse_args()

	driver=util.start_driver(args.user_data_dir)


	if args.test_set_status is not None:
		codeforces.set_status(driver, args.contest, args.test_set_status)
		return


	codeforces_contest_url=args.contest
	get_yandex_url: Dict[str, str]=dict(args.map)
	last_submissions_id: set[str]=set()
	status_lines: list[str]=[] #each element has trailing \n

	def print_status(status: str)->None:
		nonlocal status_lines
		print("======== status::", status)
		status_lines.append(status+'\n')
		status_lines=status_lines[-15:]
		codeforces.set_status(driver, codeforces_contest_url, "".join(status_lines))

	print("wait initial=", args.wait_initial)
	time.sleep(args.wait_initial)
	print("wait_initial done")

	first_iteration=True
	while True:
		if not first_iteration: time.sleep(10)
		first_iteration=False

		submissions=codeforces.get_submissions(
				driver,
				codeforces.get_status_url(codeforces_contest_url)
				)
		for codeforces_submission in submissions[::-1]:
			if codeforces_submission.id in last_submissions_id: continue
			if int(codeforces_submission.id)<=args.max_ignore: continue
			last_submissions_id.add(codeforces_submission.id)

			try: yandex_url=get_yandex_url[codeforces_submission.problem]
			except KeyError: continue

			print_status(f"{codeforces_submission.id} : received")
			
			code=codeforces.get_code(driver,
					codeforces.build_submission_url(codeforces_contest_url, codeforces_submission.id)
					)

			try:
				yandex_submission=yandex.do_submit(driver, yandex_url, code)
			except:
				traceback.print_exc()
				print_status(f"{codeforces_submission.id} : cannot submit for some reason...?")
				codeforces.do_reject(driver,
						codeforces.build_submission_url(codeforces_contest_url, codeforces_submission.id)
						)
				continue

			print_status(f"{codeforces_submission.id} : submitted")

			while yandex_submission.running:
				time.sleep(10)
				[yandex_submission]=[
						yandex_submission_new for yandex_submission_new in yandex.get_submissions(driver, yandex_url)
						if yandex_submission_new.id==yandex_submission.id]

			print_status(f"{codeforces_submission.id} : verdict {yandex_submission.verdict}")
			if not yandex_submission.correct:
				codeforces.do_reject(driver,
						codeforces.build_submission_url(codeforces_contest_url, codeforces_submission.id)
						)



if __name__=="__main__":
	main()
