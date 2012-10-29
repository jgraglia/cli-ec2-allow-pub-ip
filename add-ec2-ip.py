#!/usr/bin/python
import sys
import urllib2
import boto
import argparse
from boto.ec2.connection import EC2Connection
from time import time
from datetime import datetime

def findIP():
    '''
    simple python script to return your public IP address using whatismyip.com
    if executed from command line will display IP

    Returns your IP address. Includes setting the header to match the request
    see http://www.whatismyip.com/faq/automation.asp
    '''
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0)' \
                    + ' Gecko/20100101 Firefox/12.0' }
    return urllib2.urlopen(urllib2.Request("http://automation.whatismyip.com/n09230945.asp",None, headers )).read()

def lookupSecurityGroupByName(conn, name):
    try:
    	rs = conn.get_all_security_groups(name)
    	print "Security groups: ", len(rs), " found: ", rs
    	return rs[0]
    except boto.exception.EC2ResponseError:
	print "Error while looking for Security Group with name:", name
	rs = conn.get_all_security_groups()
	for sg in rs:
		print "   -> ", sg.name
	sys.exit(1)

def createIpRange24(ip):
    return '%s0/24' % ip[:-len(ip.split('.')[-1])]

def createIpRange32(ip):
    return '%s/32' % ip

''' ~/.boto needed or read http://docs.pythonboto.org/en/latest/boto_config_tut.html '''
def addIPSecurity(group, ports=22, dryRun=False):
    print "Args :: Group : ", group, ", TCP ports: ", ports
    conn = boto.ec2.connect_to_region("eu-west-1")
    print "Connected to", conn
    sg = lookupSecurityGroupByName(conn, group)
    print "Targeted Security Group: ", sg.name
    pub_ip = findIP()
    print "Public IP:", pub_ip
    pub_ip_range = createIpRange32(pub_ip)
    print len(sg.rules), "rules actually defined in", sg.name
    for port in args.ports:
	if dryRun:
		print "DRY RUN >> AUTH   >> ",  pub_ip_range, ", TCP: ", port
	else:
	    	sg.authorize(ip_protocol='tcp', from_port=port, to_port=port, cidr_ip=pub_ip_range)
    print "Now, ", len(sg.rules), "rules defined in", sg.name

    print "========================================================="
    print "=========== PRESS A KEY TO REMOVE RULES ================="
    print "========================================================="
    authTime=datetime.now()
    print authTime
    raw_input()
   
    print "Duration:",datetime.now()-authTime
    for port in args.ports:
	if dryRun:
		print "DRY RUN >> REVOKE  >> ",  pub_ip_range, ", TCP: ", port
	else:
	    	sg.revoke('tcp', port, port, cidr_ip=pub_ip_range)
    print "Now, ", len(sg.rules), "rules defined in", sg.name


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='CLI control of AWS EC2 Security Groups')
    parser.add_argument('-g', '--group', required=True)
    parser.add_argument('-d', '--dry', default=False, action="store_true")
    parser.add_argument('ports', metavar='p', \
		type=int, nargs='*', default = [22, 443, 80],  \
		help='a TCP port to open')
    args = parser.parse_args()
    addIPSecurity(args.group, args.ports, args.dry)
