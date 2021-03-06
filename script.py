import requests
import json
import time
from argparse import ArgumentParser
from graphviz import Digraph

parser = ArgumentParser()
parser.add_argument(dest='org', help='organization to fetch aquisitions for')
parser.add_argument('--mobile', dest='mobile', help='list mobile applications')
args = parser.parse_args()
output_file = "/Users/me/Desktop/" + args.org + ".toplevels.out"
top_level_domains = open(output_file,"w+")
output_file2 = "/Users/me/Desktop/" + args.org + ".mobileapps.out"
mobile_apps = open(output_file2,"w+")

proxies = {
	"http": "127.0.0.1:8085",
	"https": "127.0.0.1:8085"
}



def get_acq(org):
	try:
		headers = {'Accept':'application/json, text/plain, */*',
		'X-Requested-With':'XMLHttpRequest',
		#distill networks protections removed from crunch, placeholder in case it comes back
		#'X-Distil-Ajax':'vztwxdbs',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
		'Referer':'https://www.crunchbase.com/organization/walmart',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'en-US,en;q=0.9'}
		url = "https://www.crunchbase.com/v4/data/entities/organizations/"+org+"?field_ids=%5B%22identifier%22,%22layout_id%22,%22facet_ids%22,%22title%22,%22short_description%22,%22is_locked%22%5D&layout_mode=view"
		r = requests.get(url, headers=headers, proxies=proxies, verify=False)
		#throttle to not trigger distill networks protection
		time.sleep(2)
		return r.json()
	except:
		print("Not receiving valid json data")

def load_acq(file):
	json_data=open(file).read()
	data = json.loads(json_data)
	return data

def print_acq(data):
	for idx,company in enumerate(data['cards']['acquisitions_list']):
		print(idx, " ", company['acquiree_identifier']['value'])

def print_subs(data):
	for subs in data['cards']['sub_organizations_image_list']:
		print(subs['ownee_identifier']['value'])

def create_nodes(org, data):
	dot.node(org, org)
	for idx,company in enumerate(data['cards']['acquisitions_list']):
		dot.node(company['acquiree_identifier']['value'], company['acquiree_identifier']['value'], fillcolor='blue')
		dot.edge(org, company['acquiree_identifier']['value'], label='aquisition', fillcolor='blue')
	for idx,company in enumerate(data['cards']['sub_organizations_image_list']):
		dot.node(company['ownee_identifier']['value'], company['ownee_identifier']['value'], fillcolor='green')
		dot.edge(org, company['ownee_identifier']['value'], label='subsidiary', fillcolor='green')		

def process_org(org, uuid):
	#make request
	data = get_acq(uuid)

	#validate a response is correct
	try:
		test = data['cards']['acquisitions_list']
	except:
		print("Data is not accessible or " + org + "has no records")
		return

	#add primary top level domain to graph and text output if it exists in dataset otherwise skip
	try:
		site = data['cards']['overview_fields2']['website']['value']
		top_level_domains.write(site + '\n')
		dot.node(org, org + "\\n" + site)
	except:
		dot.node(org, org)
		pass

	for idx,app in enumerate(data['cards']['apptopia_app_overview_list_public']):		
		app = app['identifier']['value']
		mobile_apps.write(org + " " + app + "\n")
	for idx,company in enumerate(data['cards']['acquisitions_list']):
		dot.node(company['acquiree_identifier']['value'], company['acquiree_identifier']['value'])
		dot.edge(org, company['acquiree_identifier']['value'], label='aquisition')
	for idx,company in enumerate(data['cards']['sub_organizations_image_list']):
		dot.node(company['ownee_identifier']['value'], company['ownee_identifier']['value'])
		dot.edge(org, company['ownee_identifier']['value'], label='subsidiary')
	if(len(data['cards']['acquisitions_list']) > 0 or len(data['cards']['sub_organizations_image_list']) > 0):
		for company in data['cards']['acquisitions_list']:
			uuid = company['acquiree_identifier']['uuid']
			name = company['acquiree_identifier']['value']		
			process_org(name, uuid)
		for company in data['cards']['sub_organizations_image_list']:
			uuid = company['ownee_identifier']['uuid']
			name = company['ownee_identifier']['value']
			process_org(name, uuid)			

#initial request to get uuid
def get_start_uuid(org):
		data = get_acq(org)
		uuid = data['properties']['identifier']['uuid']
		return uuid
	
dot = Digraph(comment=args.org)
uuid = get_start_uuid(args.org)
process_org(args.org, uuid)
dot.render('tmp/' + args.org + '_map.gv', view=False)





