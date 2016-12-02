import xml.etree.cElementTree as ET
import glob
from src.core import *

def parse(files,db):
    # for path in files.split(','):
        for nmapfile in files:
            print_info("Parsing: %s"%(nmapfile))
            counter = 0
            with db:
                cur = db.cursor()        
                root = ET.parse(nmapfile).getroot()
                for host in root.findall('host'):
                    ip = host.find('./address[@addrtype="ipv4"]').get('addr')
                    for port in host.findall("./ports/port"):
                        portnr = port.get('portid')
                        protocol = port.get('protocol')
                        state = port.find('state').get('state')
                        service = 'Unknown'
                        if port.find('service') is not None:
                            service = port.find('service').get('name')
                        if 'open' in state:
                            cur.execute('''INSERT INTO IPPORTS(ip,port,protocol,state,service) VALUES(?,?,?,?,?)''',(ip,portnr,protocol,state,service))
                        counter = counter + 1
                cur.close()
            print_info_spaces("Imported %d issues"%counter)
        