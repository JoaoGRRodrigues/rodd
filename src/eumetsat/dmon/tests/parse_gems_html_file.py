'''
Created on Feb 14, 2014

@author: guillaume aubert
'''
import re
#import eumetsat.dmon.gems_feeder as gems_feeder

"GTS headers of outgoing file W_XX-EUMETSAT-Darmstadt,SOUNDING+SATELLITE,METOPB+GRAS_C_EUMP_20140211232028_07278_eps_o_thn_l1.bin: IEGX01 EUMP 112316; IEGX01 EUMP 112318; IEGX01 EUMP 112319;"

#process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 

line_expr = "[\t, ]*<td>GTS headers of outgoing file (?P<file>.*): (?P<bulletins>.*)</td>"
line_re = re.compile(line_expr)

process_expr = "GTS headers of outgoing file (?P<file>.*): (?P<bulletins>.*)"
expr_re = re.compile(process_expr)


def parse_gems_html():
    """
       Parse the Html GEMS daily file
    """
    
    #fd = open("/Users/gaubert/OneDayOfRMDCNOugoingHeaders.htm")
    #fd = open("/Users/gaubert/simple_bull.html")
    #res_fd = open("/Users/gaubert/result.csv", "w+")
    #res_fd1 = open("/Users/gaubert/result-by-headers.csv", "w+")

    fd      = open("/home/mobaxterm/DWD-Data/OneDayOfRMDCNOugoingHeaders.htm")
    res_fd  = open("/home/mobaxterm/DWD-Data/result.csv", "w+")
    res_fd1 = open("/home/mobaxterm/DWD-Data/result-by-headers.csv", "w+")
    
    
    htmlStr = ""
    
    bull_map = {}
    
    for line in fd.readlines():
        #if "<td>GTS headers" in line:
            #print("We are in \n")
        matched = line_re.match(line)
        if matched:     
            filename  = matched.group('file')
            bulletins = matched.group('bulletins')
            bull_str = bulletins.split(";")
            bull_info = []
            unique_bull = []
            res_line = "%s" % (filename)
            for bull in bull_str:
                b_info = bull.strip().split(" ")
                if len(b_info)>=2:
                    #b1 = b_info[0]
                    #b2 = b_info[1]
                    if b_info[0] not in unique_bull:
                        unique_bull.append(b_info[0])
                        bull_info.append( (b_info[0], b_info[1]) )
                        res_line += ",%s:%s" % (b_info[0], b_info[1])
                        
                        #add bulletins 
                        key = "%s:%s" % (b_info[0], b_info[1])
                        if key in bulletins:
                            l = bull_map[key]
                          
                            l.append(filename)
                        else:
                            bull_map[key] = [filename]
                        
            #print("filename = %s,\n bull_info = %s\n" % (filename, bull_info))
            res_line += "\n"
            res_fd.write(res_line)
    
    for bull in bull_map:
        line = ""
        for the_list in bull_map[bull]:
            #for elem in the_list:
            line += "%s # " % the_list
        
        res_fd1.write("%s / %s\n" % (bull, line))

def compare_EUM_DWD():
    """
       Compare EUM DWD Bulletins
    """
    the_dir = "/home/mobaxterm/DWD-Data/" 
    eum_fd = open("%s/result-by-headers.csv" %(the_dir))
    dwd_fd = open("%s/DCPC_Eumetsat.txt" % (the_dir))

    set_dwd = set()
    set_eum = set()

    eum_bull_info = {}
    dwd_bull_info = {}
    
    #read DWD Bulletins
    for line in dwd_fd.readlines():
        elems = line.split(",")
        #print("bulletin %s origin %s" % (elems[6], elems[7]))
        #set_dwd.add("%s:%s" % (elems[6][1:-1],elems[7][1:-1]))
        #print("%s:%s\n" % (elems[6][1:-1],elems[7][1:-1]))
        bull_id = "%s" % (elems[6][1:-1]) 
        
        set_dwd.add(bull_id)
        dwd_bull_info[bull_id] = elems[11]  

    #read EUM Bulletins
    for line in eum_fd.readlines():
        elems = line.split("/")
        #print("bulletins = [%s]" % (elems[0].strip()))
        bull_id = elems[0].strip().split(":")

        if len(bull_id[0]) < 6:
            print("Warning bull_id is invalid %s. Ignore it !!!\n" % (elems))
        else:
            #print("bull_id = %s" % (bull_id))
            #set_eum.add(elems[0].strip())
            set_eum.add(bull_id[0])
            eum_bull_info[bull_id[0]] = elems[1]

    in_dwd_not_in_eum = set_dwd.difference(set_eum)
    in_eum_not_in_dwd = set_eum.difference(set_dwd)

    print("total in dwd set %d, nb elem in dwd and not in eum: %d" % (len(set_dwd), len(in_dwd_not_in_eum)))
    print("total in eum set %d, nb elem in eum and not in dwd: %d" % (len(set_eum), len(in_eum_not_in_dwd)))

    #print("Bulletin IDs in EUMETSAT Bulletin outputs and not on the DWD list")

    #print("|  bullID  |        filename")
    #print("|----------------------------------------")

    #for b_id in sorted(in_eum_not_in_dwd):
    #    print("|  %s  |  %s" % (b_id, eum_bull_info[b_id].strip()))    

    print("-------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------")
    print("Bulletin IDs in DWD Bulletin outputs and not on the EUMETSAT list")

    print("|  bullID  |        filename")
    print("|----------------------------------------")

    for b_id in sorted(in_dwd_not_in_eum):
        # discard all continuations (T2 = E and ii > 1)
        if (len(b_id) >= 6 and b_id[1] == "E" and int(b_id[4:6]) > 1) or (dwd_bull_info[b_id].startswith("CONTINUATION")):
           # discard continuation
           #something to be done
           continue
        else:
           print("|  %s  |  %s" % (b_id, dwd_bull_info[b_id].strip()))

    #print("in_eum_not_in_dwd = %s" % (in_eum_not_in_dwd)) 
    

if __name__ == '__main__':
    
    #parse_gems_html() 
    compare_EUM_DWD()
