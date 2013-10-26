#!/usr/bin/python -tt

# Title: xml parser
# Note: for now, just write for permutation.xml
# Author: Brian Yang
# Last revision: 1/23/2013

import sys
import xml.dom.minidom as minidom

#---------------------------------------------------------
def getContent(xml):

    doc = minidom.parse(xml)
    node = doc.documentElement
    permutations = doc.getElementsByTagName('permutation')

    # get all the items in <permutation> ... </permutation>
    line_nums = []
    orders = []
    directives = []
    for permutation in permutations:
        line_numObj = permutation.getElementsByTagName('line_num')[0]
        orderObj = permutation.getElementsByTagName('order')[0]
        directiveObj = permutation.getElementsByTagName('directive')[0]

        line_nums.append(line_numObj)
        orders.append(orderObj)
        directives.append(directiveObj)        
        
    if len(orders)!=len(line_nums) or len(line_nums)!=len(directives):
        print 'Check the correctness of XML file!'
        sys.exit()    
        
    for i in range(0, len(orders)):
        d_nodes = directives[i].childNodes
        o_nodes = orders[i].childNodes
        ln_nodes = line_nums[i].childNodes
        
        for j in range(0, len(d_nodes)):
            # print line number
            if ln_nodes[j].nodeType == ln_nodes[j].TEXT_NODE:
                print 'LINE_NUMBER: ' + ln_nodes[j].data
            # print entire directive which can be inserted into source file
            if o_nodes[j].nodeType == o_nodes[j].TEXT_NODE and \
                    d_nodes[j].nodeType == d_nodes[j].TEXT_NODE:
                print '  DIRECTIVE: ' + d_nodes[j].data + ' ' + o_nodes[j].data + '\n'
                
                
def main():
    if len(sys.argv) < 2:
        print 'Usage: python parser.py name.xml'
        sys.exit()

    document = sys.argv[1]
    getContent(document)

# call main()
if __name__ == '__main__':
    main()
