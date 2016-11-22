import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class SiteScan(models.Model):
	Site_Name = models.CharField(max_length=200)
	Scan_Date = models.DateTimeField('date scanned')
	Scan_Completed = models.CharField(max_length=10, default='Running')
	SSL_Grade = models.CharField(max_length=3, default=0)
	SSL_SName = models.CharField(max_length=200, default=0)
	SSL_IP = models.CharField(max_length=16, default=0)
	SSL_Port = models.CharField(max_length=5, default=0)
	SSL_ServSig = models.CharField(max_length=32, default=0)
	SSL_Full = models.CharField(max_length=100, default=0)
	SSL_NIST = models.CharField(max_length=10, default=0)
	SSL_HIPAA = models.CharField(max_length=10, default=0)
	SSL_PCI = models.CharField(max_length=10, default=0)
	WhoIsDomain = models.CharField(max_length=200, default=0)
	WhoIsEmails = models.CharField(max_length=200, default=0)
	WhoIsUpdated = models.DateTimeField('Updated Date', default=timezone.now)
	WhoIsWServer = models.CharField(max_length=200, default=0)
	WhoIsCity = models.CharField(max_length=200, default=0)
	WhoIsExpiration = models.DateTimeField('Expiration Date', default=timezone.now)
	WhoIsNameServer = models.CharField(max_length=200, default=0)
	WhoIsState = models.CharField(max_length=200, default=0)
	WhoIsStatus = models.CharField(max_length=200, default=0)
	WhoIsReferral = models.CharField(max_length=200, default=0)
	WhoIsDNSSec = models.CharField(max_length=200, default=0)
	WhoIsCreation = models.DateTimeField('Creation Date', default=timezone.now)
	WhoIsOrg = models.CharField(max_length=200, default=0)
	WhoIsZip = models.CharField(max_length=200, default=0)
	WhoIsName = models.CharField(max_length=200, default=0)
	WhoIsRegistrar = models.CharField(max_length=200, default=0)
	WhoIsCountry = models.CharField(max_length=200, default=0)
	WhoIsAddress = models.CharField(max_length=200, default=0)
	EmailPattern = models.CharField(max_length=50, default=0)
	EmailsAll = models.CharField(max_length=10000, default=0)
	Traceback = models.CharField(max_length=10000, default=0)
	def __str__(self):
		return self.Site_Name
	def was_scanned_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=7) <= self.pub_date <= now

class Emails(models.Model):
	scan = models.ForeignKey(SiteScan, on_delete=models.CASCADE)
	email = models.CharField(max_length=200, default=0)
	def __str__(self):
		return self.email

class DNS(models.Model):
	scan = models.ForeignKey(SiteScan, on_delete=models.CASCADE)
	record = models.CharField(max_length=10, default=0)
	name = models.CharField(max_length=50, default=0)
	address = models.CharField(max_length=50, default=0)
	def __str__(self):
		return self.name

class ARIN(models.Model):
	scan = models.ForeignKey(SiteScan, on_delete=models.CASCADE)
	netname = models.CharField(max_length=10, default=0)
	cidr = models.CharField(max_length=50, default=0)
	def __str__(self):
		return self.cidr

class user(models.Model):
	scan = models.ForeignKey(SiteScan, on_delete=models.CASCADE)
	status = models.CharField(max_length=6, default=0)
	email = models.CharField(max_length=100, default=0)
	firstname = models.CharField(max_length=100, default=0)
	lastname = models.CharField(max_length=100, default=0)
	fullname = models.CharField(max_length=200, default=0)
	gender = models.CharField(max_length=20, default='Not Available')
	deducedlocation = models.CharField(max_length=100, default=0)
	digitalfootprint = models.CharField(max_length=500, default='Not Available')
	def __str__(self):
		return self.email

class photo(models.Model):
	email = models.ForeignKey(user, on_delete=models.CASCADE)
	ptype = models.CharField(max_length=100, default=0)
	purl = models.CharField(max_length=100, default=0)
	def __str__(self):
		return self.ptype

class organization(models.Model):
	email = models.ForeignKey(user, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, default=0)
	startDate = models.CharField(max_length=100, default=0)
	name = models.CharField(max_length=100, default=0)
	current = models.CharField(max_length=10, default=0)
	def __str__(self):
		return self.name

class socialp(models.Model):
	email = models.ForeignKey(user, on_delete=models.CASCADE)
	stype = models.CharField(max_length=100, default=0)
	url = models.CharField(max_length=100, default=0)
	following = models.CharField(max_length=10, default=0)
	followers = models.CharField(max_length=10, default=0)
	def __str__(self):
		return self.stype

class links(models.Model):
	email = models.ForeignKey(user, on_delete=models.CASCADE)
	url = models.CharField(max_length=200, default=0)

class builtwith(models.Model):
	scan = models.ForeignKey(SiteScan, on_delete=models.CASCADE)
	domain = models.CharField(max_length=200, default=0)
	subdomain = models.CharField(max_length=200, default=0)
	url = models.CharField(max_length=200, default=0)
	name = models.CharField(max_length=200, default=0)
	tag = models.CharField(max_length=200, default=0)
	description = models.CharField(max_length=1000, default=0)
	def __str__(self):
		return self.domain
