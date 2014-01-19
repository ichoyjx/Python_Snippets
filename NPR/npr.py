#!/usr/bin/python -tt
#coding:utf-8

from urllib2 import Request, urlopen, URLError

def npr():

    request = Request('http://placekitten.com/')

try:
    response = urlopen(request)
    kittens = response.read()
    print kittens[559:1000]
except URLError, e:
    print 'No kittez. Got an error code:', e

# main
def main():
    npr()

# call main()
if __name__ == '__main__':
    main()
