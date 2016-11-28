import sys, os, re, traceback
import json
import requests
import django
from bs4 import BeautifulSoup
from django.conf import settings

def cidr_brute(cidr, id, s):
	s.Scan_Completed = 'Bruteforce'
	s.save()
	os.system('dnsrecon -r %s > tempbrute.txt' % cidr)
	with open('tempbrute.txt') as f:
		content = [x.strip('[*]') for x in f.readlines()]
	content = [x.strip() for x in content]
	for i, val in enumerate(content):
		temp_brute = content[i]
		temp_brute = temp_brute.split(' ')
		s.dns_set.create(record=temp_brute[0], name=temp_brute[1], address=temp_brute[2])
	os.system('rm tempbrute.txt')
	s.Scan_Completed = 'Completed'
	s.save()
	return 0

def main():
	cidr = sys.argv[1]
	id = sys.argv[2]
	cwd = sys.argv[3]
	sys.path.append(cwd)
	os.environ['DJANGO_SETTINGS_MODULE'] = 'o_saint.settings'
	django.setup()
	from site_scan.models import SiteScan
	s = SiteScan.objects.get(pk=id)
	try:
		cidr_brute(cidr, id, s)
	except:
		s.Scan_Completed='Failed'
		s.Traceback=traceback.format_exc()
		s.save()

if __name__ == "__main__":
	main()

