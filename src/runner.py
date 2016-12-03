#!/usr/bin/env python
####################################################################################
# Main runner
####################################################################################

# main import
import os
import sqlite3 as lite
import ruamel.yaml
import subprocess
import datetime

from src.core import *
# from src.apps.base import  *

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def testreplace(input, test, value):
    result = input
    if test in input:
        result = input.replace(test,str(value))
    return result

def prepare(result, args, row):
    result = testreplace(result, '%IP',row['ip'])
    result = testreplace(result, '%PORT',row['port'])
    result = testreplace(result, '%USERLIST',args.uids)
    result = testreplace(result, '%PASSLIST',args.pwds)
    result = testreplace(result, '%SAVEDIR',args.saveDir)
    result = testreplace(result, '%BALDRICK',args.baldrick_dir)
    
    return result

def build(args, row, tests, testtype, really):
    result = list()
    if really and testtype in tests:
        for test in tests[testtype]:
            result.append(prepare(test, args, row))
    return result


def runtests(args, tests):
    total = 0
    counter = 0
    for key in tests:
        total += len(tests[key])
    for group in tests:
        print_status("Checkinging %s services..."%(group))
        if not args.debug:
            output = open("%s/%s.out"%(args.saveDir ,group),"ab")
        for test in tests[group]:
            print_info_spaces(" %s --------- Executing: %s -------------------------- "%(datetime.datetime.now().time(),test))
            if not args.debug:
                output.write("Test: %s\n\n"%test)
                output.flush()
                subprocess.Popen("%s"%test, shell=True, stderr=subprocess.STDOUT, stdout=output).wait()
                output.write("\n===========================================================================================\n\n")
                output.flush()
            counter = counter + 1
            print_info_spaces(" %s --------- Done!   (%d of %d)        -------------------------- "%(datetime.datetime.now().time(),counter,total))
        if not args.debug:
            output.close()



def buildtests(args, db):
    result = dict()
    stream = open(args.configuration,'r')
    content = ruamel.yaml.load(stream)
    stream.close()
    if args.validate or args.brute:
        for type in content.iterkeys():
            tests = list()
            with db:
                db.row_factory = dict_factory
                cur = db.cursor()  
                cur.execute("select distinct ip,port from ipports where %s"%content[type]['where']) 
                for row in cur.fetchall():
                    tests += build(args, row, content[type], 'validations', args.validate)
                    tests += build(args, row, content[type], 'bruteforce', args.brute)
            if len(tests) > 0:
                result[type] = tests
    return result


def do(args):
    print_status("Please give a customer reference: ",end="")
    args.saveDir = input()
    # Create SQLite DB to hold IP/port/protocol/state
    db = lite.connect(args.dbname)
    with db:
        cur = db.cursor()
        cur.execute('''CREATE TABLE IPPORTS(ip TEXT, port INT, protocol TEXT, state TEXT, service TEXT, UNIQUE (ip,port,protocol,state,service) ON CONFLICT REPLACE )''')
        cur.close()
    
    # Parse the various files and save them in the db
    if args.nmap:
        from src.parsers import NMapParser
        NMapParser.parse(args.nmap,db)
    if args.nessus:
        from src.parsers import NessusParser
        NessusParser.parse(args.nessus,db)
    if args.openvas:
        from src.parsers import OpenVASParser
        OpenVASParser.parse(args.openvas,db)
    
    with db:
        cur = db.cursor()
        cur.execute('''select count(distinct ip) from ipports''')
        ips = cur.fetchone()
        cur.execute('''select count(distinct ip) from ipports''')
        ports = cur.fetchone()
        print_warning("Running against %d ips and %d ports"%(ips[0],ports[0]))
        print_status('Checking for unknown services')
        cur.execute('''select count(*) from ipports where service="Unknown"''')
        if cur.fetchone() > 0:
            # we have some ports without a known service, 
            pass
        cur.close()
    
    cont = input("We're taking a break, do you want to continue? [y/n]") or 'y'
    if cont.lower() != 'y':
        print 'And .... we\'re out of here'
        exit(1)
    
    tests = buildtests(args, db)
    total = 0
    for key in tests:
        total += len(tests[key])
    print_warning("Going to execute %d tests"%(total))
    
    # Create directory to store all output
    if not os.path.exists(args.saveDir):
        os.makedirs(args.saveDir)

    runtests(args,tests)

    # change ownership of saveDir to actual user
    os.chown(args.saveDir,args.userid,args.userid)
    for root,dirs,files in os.walk(args.saveDir):
        for d in dirs:
            os.chown(d,args.userid,args.userid)
        for f in files:
            fname = os.path.join(root,f)
            os.chown(fname,args.userid,args.userid)
    

    