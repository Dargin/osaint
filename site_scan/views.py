from django.shortcuts import render, redirect, get_object_or_404
from site_scan.models import SiteScan, user
from django.utils import timezone
from site_scan.SiteGather import scan_site, fullcontact, fullcontact_new
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import shlex, subprocess
import sys, os
import re

from django.utils.safestring import mark_safe

import json

def index(request):
	return render(request, 'index.html')

def search(request):
	if request.method == "POST":
		site_to_scan = request.POST.get("site_to_scan", None)
		email = request.POST.get("email", None)
		site_email = request.POST.get("site_email", None)
		cwd = os.getcwd()
		cwd = str(cwd)
		if site_to_scan:
			time = timezone.now()
			tstring=time.strftime('%m/%d/%Y')
			sts = SiteScan(Site_Name=site_to_scan+' '+tstring, Scan_Date=time)
			sts.save()
			id = sts.id
			command = "python3 site_scan/SiteGather.py %s %s %s" % (site_to_scan, id, cwd)
			p = subprocess.Popen(command , shell=True, stdout=subprocess.PIPE)
			scannedsite = get_object_or_404(SiteScan, pk=id)
			
			return redirect('/o_saint/%s/' % id)
		elif email:
			results = fullcontact(email)
			results = re.sub("True", "true", str(results))
			return render(request, 'email.html', {'results': results})
		else:
			return redirect('o_saint:index')
	else:
		return redirect('o_saint:index')

def history(request):
	latest_scan_list = SiteScan.objects.order_by('-Scan_Date')[:20]
	template = loader.get_template('history.html')
	context = {
		'latest_scan_list': latest_scan_list,
	}
	return HttpResponse(template.render(context, request))

def details(request, scan_id):
    scan = get_object_or_404(SiteScan, pk=scan_id)
    return render(request, 'detail.html', {'scan': scan})

def ssl(request, scan_id):
	path = 'site_scan/templates/SSL/'
	complete_path = os.path.join(path, str(scan_id))
	with open(complete_path) as json_data:
		results = json.load(json_data)
	results = re.sub("True", "true", str(results))
	results = re.sub("False", "false", str(results))
	return render(request, 'ssl.html', {'results': results})

def email_quick(request):
	if request.method=='GET':
		email = request.GET.get('email')		
		results = fullcontact(email)
		truth = {'True':'true'}
		results = re.sub("True", "true", str(results))
		return render(request, 'email.html', {'results': results})

def email_detail(request):
	if request.method=='GET':
		email_val = request.GET.get('email')
		id = request.GET.get('id')
		fullcontact_new(email_val, id)
		link = email_val+"_"+str(id)	
		results = get_object_or_404(user, email=link)
		return render(request, 'email_detail.html', {'results': results})

def cidr(request):
	cwd = os.getcwd()
	cwd = str(cwd)
	if request.method=='GET':
		cidr = request.GET.get('cidr_val')
		id = request.GET.get('id')
		command = "python3 site_scan/cidr_bruteforce.py %s %s %s" % (cidr, id, cwd)
		p = subprocess.Popen(command , shell=True, stdout=subprocess.PIPE)
		scan = get_object_or_404(SiteScan, pk=id)
		return redirect('/o_saint/%s/' % id)

def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
