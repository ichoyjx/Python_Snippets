#!/usr/bin/python -tt
#coding:utf-8

from urllib2 import Request, urlopen, URLError
from xml.dom import minidom

def npr():

    try:
        request = Request('http://placekitten.com/')
        response = urlopen(request)
        kittens = response.read()
        print kittens[559:1000]
    except URLError, e:
        print 'No kittez. Got an error code:', e

def xml_parser (filename):
    f = open(filename, 'r')
    pets = minidom.parseString(f.read())
    f.close()

    names = pets.getElementsByTagName('name')
    for name in names:
	print name.firstChild.nodeValue

# main
def main():
    npr()
    xml_parser("pets.txt")

# call main()
if __name__ == '__main__':
    main()
