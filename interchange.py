#!/usr/bin/python -tt
#coding:utf-8

'''''''''''''''''''''''''''''''''''''''''''''''''''
Author: Brian Yang (brianyang1106@gmail.com)
Last revision: 2/4/2013
Note: this program will list all the combinations
      of a list to revise src files and compile
'''''''''''''''''''''''''''''''''''''''''''''''''''
# import
import os
import sys
import itertools
import xml.dom.minidom as minidom
#--------------------------------------------------
# global
pos_id = 0
size_dict = {}
line_num_dict = {}

# instructions
def instructions():
    print '\n---------------------------------------------------'
    print 'Usage 1: python dump_unroll.py unroll.f p,q,r [-st]'
    print 'Usage 2: python dump_unroll.py unroll.xml'
    print 'Description:'
    print '    unroll.f    source file'
    print '       p,q,r    nested loops will be unrolled'
    print '         -st    step execution'
    print '  unroll.xml    will use xml parser'
    print '---------------------------------------------------\n'
    sys.exit()

# system shell
def rm(filename):
    command = '/bin/rm -rf ' + filename
    os.system(command)

# compare two files
def compare(file1, file2):
    f_r1 = open(file1, 'rU')
    f_r2 = open(file2, 'rU')
    f_w = open('com_result', 'a')
    try:
        f_w.write(str(pos_id) + ',')
        # first: file size
        if os.path.getsize(file1) != os.path.getsize(file2):
            f_w.write(str(0) + '\n')
        else:
            # second: compare line by line
            flag = True
            for line1,line2 in zip(f_r1, f_r2):
                if line1 != line2:
                    flag = False
                    break

            if flag:
                f_w.write(str(1) + '\n')
            else:
                f_w.write(str(0) + '\n')
    finally:
        f_r1.close()
        f_r2.close()
        f_w.close()

# compile, execute, compare outputs    
def compile(filename, flag):
    command = 'uhf90 -O3 -LNO:minvar=off '
    if flag: # add debug options
        command += '-keep -Wb,-ttLNO:0x0004 -Wb,-trlno -flist '
    command += '__' + filename

    f_w_sh = open('test.sh','w')
    try:
        f_w_sh.write('cd ./\n' + command + '\n./a.out\nexit\n')
    finally:
        f_w_sh.close()

    os.system('/bin/sh test.sh')

    # compare the 'matrix_unroll_tmp' with 'unroll_*_ori'
    compare('matrix_unroll_tmp','matrix_' + filename + '_ori')
    
    if flag: # for step
        raw_input("\npress ENTER to continue... ")

    rm('matrix_unroll_tmp')

# compare the pragma and result file to get compile_result
def compile_result(pragma):
    tmp_list = []
    tmp_result = {}
    for elem in pragma:
        tmp_list.append(elem)
        tmp_result[elem] = 0
    
    f_w_output = open('compile_result', 'a')
    f_w_output.write(str(pos_id) + ',')
    try:
        f_r_result = open('result', 'rU')
    except IOError as e:
        # this might be redundent
        f_w_output.write('0\n') # no result
    else:
        compile_flag = False # no Result: ... output
        for line in f_r_result:
            line = line.strip('\n')
            tmp_line = line.split(',')
            if tmp_line[0] == str(pos_id):
                compile_flag = True
                for item in tmp_line:
                    # like this: ['3', 'P(u=2)', 'Q(u=4)', 'S']
                    if item.find('(u=') > 0:
                        loop_name = item[0:item.index('(')]
                        if loop_name in tmp_list:
                            equal_index = item.index('=')
                            item_usz = item[equal_index+1:len(item)-1]
                            if item_usz == str(pragma[loop_name]):
                                tmp_result[loop_name] = 1

                # check the tmp_result and write the final result
                flag = True
                for elem in tmp_result:
                    if tmp_result[elem] == 0:
                        flag = False
                        break
                if flag:
                    f_w_output.write('1\n')
                else:
                    f_w_output.write('0\n')
            else: # not the id I want
                continue
        # no compile Result:... output
        if not compile_flag:
            f_w_output.write('0\n')
        
    finally:
        f_r_result.close()
        f_w_output.close()
    return
    
# xml parser
def parser(xml):
    doc = minidom.parse(xml)
    node = doc.documentElement
    unroll = doc.getElementsByTagName('unroll')
    count = 0

    # get all the items in <unroll> ... </unroll>, within this
    # the minimum unit is <one_dir> ... </one_dir>
    for each in unroll:
        line_nums = []
        directives = []
        unroll_sizes = []
        print '\n\n--------- POS_ID = ' + str(count) + ' ---------\n'
        one_dirs = each.getElementsByTagName('one_dir')
        for one_dir in one_dirs:
            line_numObj = one_dir.getElementsByTagName('line_num')[0]
            directiveObj = one_dir.getElementsByTagName('directive')[0]
            unroll_sizeObj = one_dir.getElementsByTagName('unroll_size')[0]
            line_nums.append(line_numObj)
            directives.append(directiveObj)
            unroll_sizes.append(unroll_sizeObj)
        
        if len(directives)!=len(line_nums) or len(line_nums)!=len(unroll_sizes):
            print 'Check the correctness of XML file!'
            sys.exit()
        
        for i in range(0, len(line_nums)):
            d_nodes = directives[i].childNodes
            us_nodes = unroll_sizes[i].childNodes
            ln_nodes = line_nums[i].childNodes
        
            for j in range(0, len(d_nodes)):
                # print line number
                if ln_nodes[j].nodeType == ln_nodes[j].TEXT_NODE:
                    print 'LINE_NUMBER: ' + ln_nodes[j].data
                    # print entire directive which can be inserted into source file
                    if us_nodes[j].nodeType == us_nodes[j].TEXT_NODE and \
                      d_nodes[j].nodeType == d_nodes[j].TEXT_NODE:
                        print '  DIRECTIVE: ' + d_nodes[j].data + ' ' + us_nodes[j].data + '\n'

        count += 1
        
# generate the unroll.xml
# XML format (indent=2):                
'''
<?xml version="1.0" encoding="utf-8" ?>
<transformation>
  <unroll>
    <one_dir>
      <line_num>22</line_num>
      <directive>C*$* unroll</directive>
      <unroll_size>(2)</unroll_size>
    </one_dir>
    ...
    <one_dir>
      ...
    </one_dir>
  </unroll>
  ...
</transformation>    
'''
def generateXML(src, loop_list): # this function will be very dependent
    src = src.replace('.f', '.xml')
    xml = open(src, 'w')
    try:
        xml.write('<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n')
        xml.write('<transformation>\n')
        # main body
        for iters in range(0,3):
            dump_list = list(itertools.combinations(loop_list,iters+1))
            for pos in dump_list:
                xml.write('  <unroll>\n')
                for each_loop in pos:
                    xml.write('    <one_dir>\n')
                    xml.write('      <line_num>' + str(line_num_dict[each_loop]))
                    xml.write('</line_num>\n      <directive>C*$* unroll</directive>\n')
                    xml.write('      <unroll_size>(' + str(size_dict[each_loop]))
                    xml.write(')</unroll_size>\n    </one_dir>\n')
                xml.write('  </unroll>\n\n')
            
        # end main
        xml.write('</transformation>\n')
    finally:
        xml.close()
    return

# auto_dump will scan the source template code, 
# replace the unroll size of each loop and execute 
# the executable file whose output will be compared 
# with the original output result
def auto_dump(src, dump_list, flag):
    global pos_id
    for pos in dump_list: # positions
        f_r = open(src, 'rU')
        f_w = open('__'+src, 'w')
        f_w_be = open('count','w') # tell back-end the pos_id
        try:
            # this try block indicates processing one time
            pragma = {}
            pragma_console = []
            for index,line in enumerate(f_r):
                if line.find('@') > 0: # @p/q/r
                    tmp_loop_name = line[line.index('@') + 1] # find p/q/r

                    # line number, if error, then check the command line!
                    line_num_dict[tmp_loop_name] = index + 1
                    # replace
                    if tmp_loop_name in pos:
                        tmp_size = '@' + tmp_loop_name # @p --> 2, @q --> 4, @r --> 5
                        new_line = line.replace(tmp_size, str(size_dict[tmp_loop_name]))
                        pragma[tmp_loop_name.upper()] = size_dict[tmp_loop_name]
                        pragma_console.append(tmp_loop_name.upper() + '(u=' + \
                                              str(size_dict[tmp_loop_name]) + ')')
                        f_w.write(new_line)
                    else: # keep that line with a new line to remain the line_num
                        f_w.write('\n')
                else:
                    f_w.write(line)
                    
            # tell back-end the current pos_id
            f_w_be.write(str(pos_id))
            
        finally:
            f_r.close()
            f_w.close()
            f_w_be.close()

        # compile
        compile(src, flag)

        # output pragma to console
        print 'Pragma: ' + ','.join(pragma_console)
        print '---------------------------------\n'
        # generate pragma file
        f_w_pragma = open('pragma','a')
        f_w_pragma.write(str(pos_id) + ',' + ','.join(pragma_console) + '\n')
        f_w_pragma.close()

        # compare pragma file and result file
        compile_result(pragma)
        
        # update pos_id
        pos_id += 1

    return

# combinations dumper
def dumper(src, loops, flag):
    loop_list = loops.split(',')

    # initiate the line numbers
    # assign each loop's default unroll size
    global size_dict
    global line_num_dict
    tmp_dict = {0:2, 1:4, 2:5, 3:10, 4:3, 5:6} # after key=2, all are unexpected
    for index,elem in enumerate(loop_list):
        size_dict[elem] = tmp_dict[index] 
        line_num_dict[elem] = 0

    # clean the files will be regenerated
    rm('pragma')
    rm('result')
    rm('com_result')
    rm('compile_result')
    rm('final_result')
        
    # for a four nested loops, the innermost loop is
    # not allowed to be unrolled, so I will add the
    # directives before first three loops: 2, 4, 5
    # note that, the size of unrolling won't influence
    # the legality of result, only dependency matters.
    for iters in range(0,3): # first three loops
        dump_list = list(itertools.combinations(loop_list,iters+1))
        auto_dump(src, dump_list, flag)

    # generate the unroll.xml
    generateXML(src, loop_list)        
    return
    
# main function
def main():
    if len(sys.argv)<2 or len(sys.argv)>4:
        instructions()

    src = sys.argv[1]
    if len(sys.argv) > 2: # dumper
        second = sys.argv[2]
        if len(sys.argv)==4 and sys.argv[-1]=='-st': # step
            dumper(src, second, True)
        else: # not step
            dumper(src, second, False)
    else: # parser
        if src.find('xml') > 0:
            parser(src)
        else:
            instructions()

    os.system('python cmp.py com_result compile_result > final_result')
    return
        
# call main        
if __name__ == '__main__':
    main()
