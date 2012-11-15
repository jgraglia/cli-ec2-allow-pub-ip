#!/usr/bin/python
import sys
import urllib2
import logging
import boto
import argparse
from boto.ec2.connection import EC2Connection
from time import time
from datetime import datetime

''' WARN : Boto seems to require Python 2.x '''

'''
Public IP "providers" :
    http://agentgatech.appspot.com/
    http://automation.whatismyip.com/n09230945.asp
'''

class WhatIsMyIpRetriever(object):
	def __str__( self ):
		return "http://automation.whatismyip.com/n09230945.asp"

	def retrievePublicIp(self): 
	    '''
	    Includes setting the header to match the request
	    see http://www.whatismyip.com/faq/automation.asp
	    '''
	    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0' }
	    return urllib2.urlopen(urllib2.Request("http://automation.whatismyip.com/n09230945.asp", None, headers )).read()

class AgentGatechIpRetriever(object):
	def __str__( self ):
		return "http://agentgatech.appspot.com/"
	def retrievePublicIp(self): 
	    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0' }
	    return urllib2.urlopen(urllib2.Request("http://agentgatech.appspot.com/", None, headers)).read()

class DryRuleActivator(object):
	def __init__(self, securityGroup):
		pass
	def authorize(self, pub_ip_range, tcpPort):
		logging.info("DRY RUN >> AUTH    >> %s, TCP: %s", pub_ip_range, tcpPort)
	def revoke(self, pub_ip_range, tcpPort):
		logging.info("DRY RUN >> REVOKE  >> %s, TCP: %s", pub_ip_range, tcpPort)

class DefaultRuleActivator(object):
	def __init__(self, securityGroup):
		self.securityGroup=securityGroup
	def authorize(self, pub_ip_range, tcpPort):
		logging.info("        >> AUTH    >> %s, TCP: %s", pub_ip_range, tcpPort)
	    	try:
			res = self.securityGroup.authorize(ip_protocol='tcp', from_port=tcpPort, to_port=tcpPort, cidr_ip=pub_ip_range)
			logging.info("                  %s", res)
		except boto.exception.EC2ResponseError as e:
			logging.error("EC2 error while activating rule: %r", e)
			logging.error("ERROR with %s and %s- Press a key to ignore or CTRL+C", pub_ip_range, tcpPort)
			raw_input()
			
	def revoke(self, pub_ip_range, tcpPort):
		logging.info("        >> REVOKE  >> %s, TCP: %s", pub_ip_range, tcpPort)
		res = self.securityGroup.revoke('tcp', tcpPort, tcpPort, cidr_ip=pub_ip_range)
		logging.info("                  %s", res)

def lookupSecurityGroupByName(conn, name):
	try:
		rs = conn.get_all_security_groups(name)
		logging.info("Security groups: %s found: %s ", len(rs), rs)
		return rs[0]
	except boto.exception.EC2ResponseError as e:
		logging.error ("Error while looking for Security Group with name: %s : %r", name, e)
	rs = conn.get_all_security_groups()
	for sg in rs:
		logging.info("   -> %s", sg.name)
	sys.exit(1)

#http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
def createIpRange24(ip):
    return '%s0/24' % ip[:-len(ip.split('.')[-1])]

#http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
def createIpRange32(ip):
    return '%s/32' % ip

''' ~/.boto needed or read http://docs.pythonboto.org/en/latest/boto_config_tut.html '''
def addIPSecurity(group, ports=22, dryRun=False):
    logging.info("Args >> Group: %s, TCP ports: %s", group, ports)
    conn = boto.ec2.connect_to_region("eu-west-1")
    logging.info("Connected to %s", conn)
    sg = lookupSecurityGroupByName(conn, group)
    logging.info("Targeted Security Group: %s ", sg.name)
    instances = sg.instances()
    logging.info("%s instances will be affected", len(instances))
    for instance in instances:
        logging.info("  -> EC2 Instance: %s %s %s %s started at %s ", instance.id, instance.public_dns_name, instance.state, instance.instance_type, instance.launch_time)
    publicIpRetriever = AgentGatechIpRetriever()
    pub_ip = publicIpRetriever.retrievePublicIp()
    logging.info("Current public IP: %s (retrieved by %s)",pub_ip, publicIpRetriever)
    pub_ip_range = createIpRange32(pub_ip)
    logging.info("%s rules actually defined in %s", len(sg.rules), sg.name)
    for rule in sg.rules:
        logging.info("    %s", rule)
    ruleActivator = DryRuleActivator(sg) if dryRun else DefaultRuleActivator(sg)
    for port in args.ports:
        ruleActivator.authorize(pub_ip_range, port)
    logging.info("Now, %s rules defined in %s", len(sg.rules), sg.name)

    logging.info("=========================================================")
    logging.info("=========== PRESS A KEY TO REVOKE RULES =================")
    logging.info("=========================================================")
    authTime=datetime.now()
    logging.info("Start time: %s", authTime)
    raw_input()
   
    logging.info("Duration: %s", datetime.now() - authTime)
    for port in args.ports:
        ruleActivator.revoke(pub_ip_range, port)
    logging.info("Now, %s rules defined in %s", len(sg.rules), sg.name)


if __name__=="__main__":
	logging.basicConfig(level=logging.INFO)
	parser = argparse.ArgumentParser(description='CLI control of AWS EC2 Security Groups', epilog="Example: add-ec2-ip.py -g mygroup 22 443 8080")
	parser.add_argument('-g', '--group', required=True)
	parser.add_argument('-d', '--dry', default=False, action="store_true")
	parser.add_argument('ports', metavar='p', \
		type=int, nargs='*', default = [22, 443, 80],  \
		help='a TCP port to open. You can add many of them')
	args = parser.parse_args()
	addIPSecurity(args.group, args.ports, args.dry)
