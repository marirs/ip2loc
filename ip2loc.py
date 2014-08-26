#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Description:
    Take input of a single IP or multiple ip addresses from a file and pass it to telize api to
    determine the details of the IP, like ASN,ISP,LATITUDE,LONGITUDE, etc.

Requirements:
    1) requests (pip install requests OR sudo easy_install requests)

"""
from optparse import OptionParser
import os, sys, socket, logging, csv
import requests, json

__author__ = 'Sriram G'
__version__ = '1'
__license__ = 'GPLv3'

"""
Global variables
"""
UA = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
quiet_mode = False
logger = logging.getLogger('ip2loc.py')
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(levelname)-7s] %(asctime)s | %(message)s', datefmt='%I:%M:%S %p') #%m/%d/%Y


def uniq(_1colList):
    """
    Uniquify a list that has a single column
    """
    return  [l for i,l in enumerate(_1colList) if l not in _1colList[i+1:]]

def ip2loc(ip_list=[]):
    """
    accepts a single ip or list of ip's as a list
    and get the extra information of the ip address from telize.com api
    """
    logger.debug("ip2loc().ip2map.py...starts getting ip info for %s ips"%str(len(ip_list)))
    api_url = "http://www.telize.com/geoip/%s"
    headers = {'User-Agent': UA}
    ip2loc_list = []
    for ip in ip_list:
        """ip, country_code, country_code3, country, region_code, region, city,
	    postal_code, continent_code, latitude, longitude, dma_code, area_code, asn, isp, timezone
        """
        response = requests.get(api_url % ip, headers=headers)
        json_data = json.loads(response.text)
        try: country_code2= json.dumps(json_data["country_code"]).replace('"',"").strip()
        except KeyError: country_code2= 'N/A'
        try: country_code3= json.dumps(json_data["country_code3"]).replace('"',"").strip()
        except KeyError: country_code3= 'N/A'
        try: country= json.dumps(json_data["country"]).replace('"',"").strip()
        except KeyError: country= 'N/A'
        try: city= json.dumps(json_data["city"]).replace('"',"").strip()
        except KeyError: city= 'N/A'
        try: region= json.dumps(json_data["region"]).replace('"',"").strip()
        except KeyError: region= 'N/A'
        try: region_code= json.dumps(json_data["region_code"]).replace('"',"").strip()
        except KeyError: region_code= 'N/A'
        try: lat= json.dumps(json_data["latitude"]).replace('"',"").strip()
        except KeyError: lat= 'N/A'
        try: lng= json.dumps(json_data["longitude"]).replace('"',"").strip()
        except KeyError: lng= 'N/A'
        try: zip= json.dumps(json_data["postal_code"]).replace('"',"").strip()
        except KeyError: zip= 'N/A'
        try: isp= json.dumps(json_data["isp"]).replace('"',"").strip()
        except KeyError: isp= 'N/A'
        try: asn= json.dumps(json_data["asn"]).replace('"',"").strip()
        except KeyError: asn= 'N/A'

        t = [ip,lat,lng,country_code2,country_code3,country,region_code,region,city,zip,asn,isp]
        ip2loc_list.append(t)
    logger.debug("ip2loc().ip2map.py...finished")
    """
    returns:
    ipaddress, latitude, longitude, country_code2, country_code3, country, region_code, region, city, postal_code, asn, isp
    """
    return ip2loc_list


def main():
    """
    main function
    """
    all_ips = []
    processed = []
    pCSV = csv.writer(sys.stdout)
    parser = OptionParser()
    parser = OptionParser(usage="usage: %prog <ip_address|file> [options] ", version="%prog v1")
    parser.add_option("-q","--quiet",action="store_true",dest="quiet_mode",help="execute the program silently",default=False)
    (options, args) = parser.parse_args()
    quiet_mode = options.quiet_mode
    csvHeader = ['ipaddress', 'latitude', 'longitude', 'country_code2', 'country_code3', 'country', 'region_code', 'region', 'city', 'postal_code', 'asn', 'isp']
    processed.append(csvHeader)

    # check to see if we got a IP Address or a File with batch ip's
    if len(args) == 1:
        #1 argument found, check to see if its a IP address
        try:
            socket.inet_aton(args[0])
            all_ips.append(args[0])
        except socket.error:
            # not a ip address, but check to see if its a valid file
            if os.path.isfile(args[0]):
                # Read from File (mostly batch)
                logger.debug("Reading from file...")
                # read the ip addresses
                ips = [line.strip() for line in open(args[0],"rU")]
                logger.debug("Total Ip's read: %s"%str(len(ips)))
                all_ips = uniq(ips)
                logger.debug("Unique Ip's to process: %s"%str(len(all_ips)))
                # Got all the ip's from the file
            else:
                print "No valid ip address or file provided"
                parser.print_help()
                sys.exit(0)
    else:
        print "No valid ip address or file provided"
        parser.print_help()
        sys.exit(0)

    logger.info("Gathering information...")
    processed += ip2loc(all_ips)

    #print processed
    [pCSV.writerow(row) for row in processed]

if __name__ == '__main__':
    main()

