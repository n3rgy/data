#!/usr/bin/python3


# Copyright 2020 by Matthew Roderick, n3rgy data ltd.
# All rights reserved.
#
# Sample script to interact with https://data.n3rgy.com service
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES ANY KIND, either express or implied.
#

import requests, json, time, csv
import argparse, sys


url="https://api-v2.data.n3rgy.com/find-mpxn/"
postdata={}
outputfile=''


#
# Arguement parsing
#
parser = argparse.ArgumentParser()
parser.add_argument("--mpxns", "-m", help="Read file with MPxNS")
parser.add_argument("--outfile","-o", help="Write to outfile")
parser.add_argument("--api","-a", help="API Key", required=True)
args = parser.parse_args()

headers= {'x-api-key':args.api}

if args.mpxns:
	f = open(args.mpxns,"r")
	mpxns = f.read().splitlines()
	f.close()

if args.outfile:
	outputfile=args.outfile
	f = open(outputfile, 'w')

try:
	postdata
except:	
	parser.print_help()
	exit(1)


count=0
tcount=0
for m in mpxns:

	rdata = requests.get( url + m, headers=headers )

	tcount += 1
	if (rdata.status_code == 200):
		result =  m + ",TRUE"
		count += 1
	else:
		result =  m + ",FALSE"
	
	if outputfile == "":
		print(result)
	else:
		f.write(result + '\n')

	if (tcount % 10 == 0):
		sys.stdout.write(".")
		sys.stdout.flush()

print("Found " + str(count) + " from total of " + str(tcount))
f.close()
	

