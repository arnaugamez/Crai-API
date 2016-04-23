#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from crai_api import *
 
def main():
	"""
	We will use login through barcode and pin
	"""
	cred = cred_from_file()
	session = SessionCrai(cred[0], cred[1], True)
	session.renew_all()
	session.close_session()

def cred_from_file(filename = os.path.dirname(os.path.abspath(__file__))+'/data/config.cfg'):
	f = open(filename, 'r')
	data = f.readlines()
	id, pwd = data[0][:-1], data[1][:-1]
	f.close()
	return id, pwd
 
if __name__ == '__main__':
	main()
