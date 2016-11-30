import string, sys, os
import shodan
import requests
import django
from django.conf import settings

def shodan_check(search, api, s):
	from o_saint import config as cfg
	shodan_key = cfg.shodan_api
	api = shodan.Shodan(shodan_key)
	search = 'net:'+search
	results = api.search(search)
	try:
		s.shodan_results=results['total']
		for result in results['matches']:
			s.shodandata_set.create(IP=result['ip_str'], hostnames=result['hostnames'], data=result['data'], port=result['port'])
		s.Scan_Completed = 'Completed'
		s.save()
	except :
		s.Scan_Complted = 'Failed'
		s.save()

def main():
	search = sys.argv[1]
	id = sys.argv[2]
	cwd = sys.argv[3]
	sys.path.append(cwd)
	os.environ['DJANGO_SETTINGS_MODULE'] = 'o_saint.settings'
	django.setup()
	from o_saint import config as cfg
	from site_scan.models import SiteScan
	s = SiteScan.objects.get(pk=id)
	shodan_key = cfg.shodan_api
	api = shodan.Shodan(shodan_key)
	shodan_check(search, api, s)

if __name__ == "__main__":
	main()
