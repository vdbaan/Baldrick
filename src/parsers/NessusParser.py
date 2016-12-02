import xml.etree.cElementTree as ET
import glob
from src.core import *

def parse(files,db):
    # for path in files.split(','):
        print(files)
        for nessusfile in files:
            print_info("Parsing: %s"%(nessusfile))
            counter = 0
            with db:
                cur = db.cursor()
                root = ET.parse(nessusfile).getroot()
                state = 'open'
                for host in root.findall('./Report/ReportHost'):
                    ip = host.find("HostProperties/tag[@name='host-ip']").text
                    for item in host.findall('ReportItem'):
                        port = item.get('port')
                        protocol = item.get('protocol')
                        service = item.get('svc_name')
                        if 'www' == service:
                            # print item.find('plugin_output').text
                            if 'SSL : yes' in item.find('plugin_output').text:
                                print 'found https'
                                service = 'https'
                            else:
                                service = 'http'
                        # cur.execute('''CREATE TABLE IPPORTS(id INT, scanner TEXT, ip TEXT, port INT, protocol TEXT, state TEXT)''')
                        cur.execute('''INSERT INTO IPPORTS(ip,port,protocol,state,service) VALUES(?,?,?,?,?)''',(ip,port,protocol,state,service))
                        counter = counter + 1
                cur.close()
            print_info_spaces("Imported %d issues"%counter)
        