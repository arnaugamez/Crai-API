#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, bs4
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class LoginError(Exception):
	pass

class SessionCrai:
	"""
	We want to store the login_request for their use on the renew
	and get/set user data methods.
	
	We will also may want to store last_request done to future
	uses on parsing information.
	
	It will attempt to login by default.
	"""

	def __init__(self, id, pwd, uses_barcode = False):
		self.open_session()
		self.login_request = None
		self.last_request = None

		try:
			self.login(id, pwd, uses_barcode)
			print "Logged correctly"
			self.profile_url = self.login_request.url
		
		except LoginError:
			print "Cannot login. Check your credentials"

	def open_session(self):
		self.session = requests.session()

	def close_session(self):
		self.session.close()

	def getLastRequest(self):
		return self.last_request

	def getLoginRequest(self):
		return self.login_request

	def login(self, id, pwd, uses_barcode):
		
		#Request's information
		login_url = "https://cataleg.ub.edu/patroninfo"

		if uses_barcode:
			login_payload = {
				'login': 'idLocal',
				'code': id,
				'pin': pwd
			}
		
		else:
			login_payload = {
				'login': 'idLocal',
				'extpatid': id,
				'extpatpw': pwd
			}

		#Making the request
		self.login_request = self.session.post(login_url, login_payload, verify=False)
		self.last_request = self.login_request

		#print 'login status code:', login_request.status_code

		if "errorMessage" in self.login_request.text:
			raise LoginError

	def renew_all(self):

		#Request's information
		renew_url = self.login_request.url

		renew_payload = {
			'currentsortorder': 'current_checkout',
			'renewall': 'YES',
			'currentsortorder': 'current_checkout'
		}

		#Making the request
		self.last_request = self.session.post(renew_url, renew_payload, verify=False)

	def getBooks(self):
		s = ''
		profile_request = self.session.get(self.profile_url)
		soup = bs4.BeautifulSoup(profile_request.text)
		
		for book in soup.find_all('tr', {'class': 'patFuncEntry'}):
			title = book.find('span', {'class': 'patFuncTitleMain'}).getText()
			expires = book.find('td', {'class': 'patFuncStatus'}).getText()
			s += title + ' ' + expires 

		return s
	
	def getAccountInfo(self):
		s = ''
		profile_request = self.session.get(self.profile_url)
		soup = bs4.BeautifulSoup(profile_request.text)
		info = soup.find('div', {'class': 'patNameAddress'}).getText()
		
		return info
	
	
	def getUserData(self):

		name = self.parseInfoName(self.login_request.text)

		data_url = self.login_request.url.replace('top', 'modpinfo')
		get_data_req = self.session.get(data_url)
		self.last_request = get_data_req

		info_data = self.parseInfoData(get_data_req.text)
		address, phone, mail = info_data[0], info_data[1], info_data[2]

		info = "\nName: " + name
		info += "\nAddress: " + address
		info += "\nPhone: " + phone
		info += "\nMail: " + mail

		return info

	def parseInfoName(text):
		lines = text.split('\n')
		for line in lines:
			if "You are logged into" in line:
				nameLine = line
				break

		name = nameLine.split('ns as ')[-1].split('<')[0]
		return name

	def parseInfoData(text):
		lines = text.split('\n')
		for line in lines[:]:
			if 'value="' not in line or 'value=""' in line:
				lines.remove(line)

		address = ""
		phone = ""
		mail = ""

		for line in lines:
			beforeValue, fromValue = line.split('value="')[0], line.split('value="')[1]
			content = ""
			i = 0
			while fromValue[i] != '"':
				content += fromValue[i]
				i+=1

			if 'addr1a' in beforeValue:
				address += content

			elif 'addr1b' in beforeValue or 'addr1c' in beforeValue or 'addr1d' in beforeValue:
				address += " - " + content

			elif 'tele1' in beforeValue:
				phone += content

			elif 'tele2' in beforeValue:
				phone += " - " + content

			elif 'email' in beforeValue:
				mail += content

		return address, phone, mail

	def setUserData(self, addr1a, addr1b, addr1c, addr1d, tele1, tele2, email):

		data_url = self.login_request.url.replace('top', 'modpinfo')
		set_data_payload = {
			'addr1a':addr1a,
			'addr1b':addr1b,
			'addr1c':addr1c,
			'addr1d':addr1d,
			'tele1':tele1,
			'tele2':tele2,
			'email':email
		}

		self.last_request = self.session.post(data_url, set_data_payload, verify=False)
