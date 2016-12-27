import sys, os, re, traceback
import subprocess
import json
import requests
import django
import whois
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from time import sleep


def scan_site(site, id, s):
	new_site = 'www.'+site
	SSLInfo = check_ssl_htbsecurity(new_site, id)
	s.SSL_Grade = SSLInfo['results']['grade']
	s.SSL_SName = SSLInfo['server_info']['hostname']['value']
	s.SSL_IP = SSLInfo['server_info']['ip']['value']
	s.SSL_Port = SSLInfo['server_info']['port']['value']
	s.SSL_ServSig = SSLInfo['server_info']['server_signature']['value']
	s.SSL_NIST = SSLInfo['nist']['compliant']['value']
	s.SSL_HIPAA = SSLInfo['hipaa']['compliant']['value']
	s.SSL_PCI = SSLInfo['pci_dss']['compliant']['value']
	s.Scan_Completed = 'Running'
	s.save()
	return 0

def check_ssl_htbsecurity(site, id):
	headers = {}
	headers['Content-Type'] = "application/x-www-form-urlencoded"
	data='domain=%s&dnsr=off&recheck=false' % site
	req = requests.post('https://www.htbridge.com/ssl/api/v1/check/1451425590.html', headers=headers , data=data)
	results = req.json()
	path = 'site_scan/templates/SSL/'
	complete_path = os.path.join(path, str(id))
	with open(complete_path, 'w') as outfile:
		json.dump(results, outfile)
	return results

def whoischeck(site, id, s):
	w = whois.whois(site)
	if 'whois_server' in w.keys():
		s.WhoIsDomain = w['domain_name']
		s.WhoIsEmails = w['emails']
		s.WhoIsWServer = w['whois_server']
		s.WhoIsCity = w['city']
		s.WhoIsNameServer = w['name_servers']
		s.WhoIsState = w['state']
		s.WhoIsStatus = w['status']
		s.WhoIsReferral = w['referral_url']
		s.WhoIsDNSSec = w['dnssec']
		s.WhoIsOrg = w['org']
		s.WhoIsZip = w['zipcode']
		s.WhoIsName = w['name']
		s.WhoIsRegistrar = w['registrar']
		s.WhoIsCountry = w['country']
		s.WhoIsAddress = w['address']
		sleep(0.5)
		s.save()
	return 0

def fullcontact(email):
	from o_saint import config as cfg
	req = requests.get("https://api.fullcontact.com/v2/person.json?email=%s&apiKey=%s" % (email, cfg.fullcontact_api))
	data = req.json()
	return data

def fullcontact_new(email_val, id):
	link = email_val+"_"+str(id)
	from site_scan.models import user
	from o_saint import config as cfg
	e = user.objects.get(email=link)
	all_topics = []
	if e.status == '0':
		req = requests.get("https://api.fullcontact.com/v2/person.json?email=%s&apiKey=%s" % (email_val, cfg.fullcontact_api))
		data = req.json()
		e.status = data['status']
		if 'contactInfo' in data.keys():	
			e.firstname = data['contactInfo']['givenName']
			e.lastname = data['contactInfo']['familyName']
			e.fullname = data['contactInfo']['fullName']
		if 'demographics' in data.keys():
			if 'locationGeneral' in data['demographics']:
				e.deducedlocation = data['demographics']['locationGeneral']
			if 'gender' in data['demographics']:
				e.gender = data['demographics']['gender']
		if 'photos' in data.keys():
			for photoloop in data['photos']:
				e.photo_set.create(ptype=photoloop['type'], purl=photoloop['url'])
		if 'digitalFootprint' in data.keys():
			for topics in data['digitalFootprint']['topics']:
				all_topics.append(topics['value'])
			e.digitalfootprint = all_topics
		if 'organizations' in data.keys():
			for org in data['organizations']:
				e.organization_set.create(title=org['title'], startDate=org['startDate'], name=org['name'], current=org['current'])
		if 'socialProfiles' in data.keys():
			for profile in data['socialProfiles']:
				if 'following' in profile.keys():
					e.socialp_set.create(stype=profile['type'], url=profile['url'], following=profile['following'], followers=profile['followers'])
				else:
					e.socialp_set.create(stype=profile['type'], url=profile['url'])
		e.save()
		all_urls = ["None found"]
		slideshare = requests.get('http://www.slideshare.net/search/slideshow?q=%s'%(email_val))
		clean=BeautifulSoup(slideshare.content, "lxml")
		search=clean.findAll('a',{'class':'title title-link antialiased j-slideshow-title'})
		if search:
			all_urls = ['']
			for at in search:
				e.links_set.create(url="http://www.slideshare.net"+at['href'])
		e.save()
	return 0	

def emailhunter(site, id, s):
	from site_scan.models import user
	from o_saint import config as cfg
	req = requests.get("https://api.emailhunter.co/v1/search?api_key=%s&domain=%s" % (cfg.email_hunter, site))
	results = req.json()
	s.EmailPattern = str(results['pattern'])
	if 'emails' in results.keys():
		for emailloop in results['emails']:
			s.emails_set.create(email=emailloop['value'])
			link = emailloop['value']+"_"+str(id)
			s.user_set.create(email=link)
			e = user.objects.get(email=link)
			for uriloop in emailloop['sources']:
				e.links_set.create(url=uriloop['uri'])
			e.save()
	s.save()
	return results

def dns_scan(site, id, s):
	os.system('dnsrecon -t brt -d %s > tempdns.txt' % site)
	os.system('dnsrecon -t std -d %s >> tempdns.txt' % site)
	with open('tempdns.txt') as f:
		content = [x.strip('[*]') for x in f.readlines()]
	content = [x.strip() for x in content]
	for i, val in enumerate(content):
		temp_dns = content[i]
		temp_dns = temp_dns.split(' ')
		s.dns_set.create(record=temp_dns[0], name=temp_dns[1], address=temp_dns[2])
		arin_scan(temp_dns[2], id, s)
	os.system('rm tempdns.txt')
	s.save()
	return 0

def arin_scan(address, id, s):
	temp = ["",""]
	temp2 = ["",""]
	os.system('whois %s > temp_whois.txt' % address)
	for line in open('temp_whois.txt', 'r'):
		if re.search('CIDR', line):
			temp = line
			temp = temp.strip()
			temp = temp.split()
			for line2 in open('temp_whois.txt', 'r'):
				if re.search('NetName', line2):
					temp2 = line2
					temp2 = temp2.strip()
					temp2 = temp2.split()
	os.system('rm temp_whois.txt')
	if temp[0] == "":
		return 0
	else:	
		cidr_val = temp[1]
		netname_val = temp2[1]
		cidr_check(cidr_val, netname_val, id, s)
		return 0

def cidr_check(cidr_val, netname_val, id, s):
	a = s.arin_set.all()
	while True:
		try:
			a.get(cidr=cidr_val)
			break
		except:
			s.arin_set.create(netname=netname_val, cidr=cidr_val)
			s.save()
			break
	return 0

def builtwith(site, id, s):
	from o_saint import config as cfg
	req = requests.get("https://api.builtwith.com/v11/api.json?KEY=%s&LOOKUP=%s" % (cfg.builtwith_api, site))
	results = req.json()
	results = results['Results']
	results = results[0]
	if results['Meta']['Names'] != None:
		for email in results['Meta']['Names']:
			s.emails_set.create(email=email['Email'])
	if results['Meta']['Emails'] != None:
		for emails in results['Meta']['Emails']:
			s.emails_set.create(email=emails)
	s.save()
	paths = results['Result']['Paths']
	i=0
	for items in paths:
		ind_path = paths[i]
		technologies = ind_path['Technologies']
		for detail in technologies:
			s.builtwith_set.create(domain=items['Domain'], subdomain=items['SubDomain'], url=items['Url'], name=detail['Name'], tag=detail['Tag'], description=detail['Description'])
		i+=1
	s.Scan_Completed = 'Completed'
	s.save()
	return 0
		

def main():
	site = sys.argv[1]
	id = sys.argv[2]
	cwd = sys.argv[3]
	sys.path.append(cwd)
	os.environ['DJANGO_SETTINGS_MODULE'] = 'o_saint.settings'
	django.setup()
	from site_scan.models import SiteScan
	s = SiteScan.objects.get(pk=id)
	try:
		scan_site(site, id, s)
		whoischeck(site, id, s)
		emailhunter(site, id, s)
		dns_scan(site, id, s)
		builtwith(site, id, s)
	except:
		s.Scan_Completed='Failed'
		s.Traceback=traceback.format_exc()
		s.save()

if __name__ == "__main__":
	main()

