'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''

import os
import datetime
import sys
import re

import multitail
import tellicastlog_parser
import xferlog_parser

import eumetsat.dmon.common.mem_db as mem_db
import eumetsat.dmon.common.time_utils as time_utils
import eumetsat.dmon.common.utils as utils
import eumetsat.dmon.common.log_utils  as log_utils

import curses
import time

LOG = None

class CurseDisplay(object):
    '''
       A simple Curse display
    '''
    def __init__(self):
        """
           constructor
        """
        self._full_screen = curses.initscr()
        #get screen size
        self._maxy, self._maxx = self._full_screen.getmaxyx()
        
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
        self._full_screen.keypad(1)
        
        self._full_screen.bkgd(curses.color_pair(1))
        self._full_screen.box()
        self._full_screen.refresh()
        # to have non blocking getch
        self._full_screen.nodelay(1)
         
        LOG.debug("maxy = %d, maxx = %d\n" %(self._maxy, self._maxx))
        
        self._active_pad   = curses.newpad(1000, 1000)
        self._finished_pad = curses.newpad(1000, 1000)
        
        
    def check_for_input(self):
        """
           Check for inputs
        """  
        c = self._full_screen.getch()
        if c in [ord('x'),ord('q')]:
            #QUIT
            return "QUIT"
        else:
            return None
    
    def print_screen(self, a_db):
        """
           print on screen
        """
        #constants to be put in files
        nb_max_active_records   = 70
        nb_max_finished_records = 30
        sleep_time = 2
        
        
        active_pad   = self._active_pad
        finished_pad = self._finished_pad
        
        header_active   = "-ACTIVE-----------------------------------------------------------------------------------------------------------------------------------------------------------"
        header_finished = "-FINISHED---------------------------------------------------------------------------------------------------------------------------------------------------------"
        header          = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |       sent      |"
        template = "%s|%s|%s|%s|%s|%s|%s|"
        
        #print(header)
        active_pad.addstr(1, 1, header_active)
        active_pad.addstr(2, 1, header)
        active_printed_records = 0
        
        finished_pad.addstr(1, 1, header_finished)
        finished_pad.addstr(2, 1, header)
        finished_printed_records = 0
        
        #set x 
        x_active   = 3
        x_finished = 3
        
        nb_recs = len(a_db)
        
        LOG.info("------ start Printing on screen ------")
        
        #reverse iteration from the lastest records to the oldest one
        while nb_recs > 0:  
            
            record = a_db.get_by_id(nb_recs-1,None)
            
            if record:          
                #reduce filename and jobname size to 50
                filename = record['filename']
                if filename:
                    filename = os.path.basename(filename)
                    
                    #will not fail if name < 50
                    filename = filename[:50]
                else:
                    filename = "-"
                
                jobname = record['jobname']
                if jobname:
                    #will not fail if name < 20
                    jobelems = jobname.split('-')
                    jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
                else:
                    jobname = "-"
                
                uplinked = record.get('uplinked', None)
                if not uplinked:
                    uplinked = "-"
                else:
                    uplinked = time_utils.datetime_to_compactdate(uplinked)
                    
                queued   = record.get('queued', None)
                if not queued:
                    queued = "-"
                else:
                    queued = time_utils.datetime_to_compactdate(queued)
                
                annouc   = record.get('announced', None)
                if not annouc:
                    annouc = "-"
                else:
                    annouc = time_utils.datetime_to_compactdate(annouc)
                    
                blocked   = record.get('blocked', None)
                if not blocked:
                    blocked = "-"
                else:
                    blocked = time_utils.datetime_to_compactdate(blocked)
                    
                    
                #dissociate active from finished part
                
                finished = record.get('finished', None)
                
                #active
                if not finished:
                    finished = "-"        
                else:
                    finished = time_utils.datetime_to_compactdate(finished)
                
                s = template % (filename.ljust(50) if filename != '-' else filename.center(50), \
                                uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17))
                
                #add records to be printed in the right area
                #it means this is active    
                if finished == "-":
                    if active_printed_records < nb_max_active_records:
                        #insert record to be printed
                        active_pad.addstr(x_active, 1, s )
                        x_active += 1
                        active_printed_records +=1
                else:
                    #finished
                    if finished_printed_records < nb_max_finished_records:
                        #insert record to be printed
                        finished_pad.addstr(x_finished, 1, s )
                        x_finished += 1
                        finished_printed_records +=1
            
            #decrement nb_recs
            nb_recs -= 1
            
        finished_pad.noutrefresh(1, 1, int(round((self._maxy-2)*(2.00/3)))+1 , 1, self._maxy-2, self._maxx-2)
        active_pad.noutrefresh(1, 1, 1, 1, int(round(self._maxy-2)*(2.00/3)) , self._maxx-2)
        
        curses.doupdate()
        
        
        LOG.info("------ End Printing on screen ------")

        #sleep x secs for the moment
        time.sleep(sleep_time)
        
    
    def reset_screen(self):
        """
        """
        curses.nocbreak()
        self._full_screen.keypad(0)
        curses.echo()
        curses.endwin()


class TextDisplay(object):
    '''
       A simple text display
    '''
    def __init__(self):
        """
           constructor
        """
        pass
    
    def check_for_input(self):
        """
           Check for inputs
        """  
        return None

    def print_screen(self, a_db):
        """
          print a table
        """
        header_Active   = "--Active----------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        header_Finished = "--Finished--------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        
        header          = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |\n"
        
        template = "%s|%s|%s|%s|%s|%s|%s|\n"
        
        active_data = header_Active   + header
        finish_data = header_Finished + header
        
        for record in a_db:
            
            #reduce filename and jobname size to 50
            filename = record['filename']
            if filename:
                filename = os.path.basename(filename)
                
                #will not fail if name < 50
                filename = filename[:50]
            else:
                filename = "-"
            
            jobname = record['jobname']
            if jobname:
                #will not fail if name < 20
                jobelems = jobname.split('-')
                jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
            else:
                jobname = "-"
            
            uplinked = record.get('uplinked', None)
            if not uplinked:
                uplinked = "-"
            else:
                uplinked = time_utils.datetime_to_compactdate(uplinked)
                
            queued   = record.get('queued', None)
            if not queued:
                queued = "-"
            else:
                queued = time_utils.datetime_to_compactdate(queued)
            
            annouc   = record.get('announced', None)
            if not annouc:
                annouc = "-"
            else:
                annouc = time_utils.datetime_to_compactdate(annouc)
                
            blocked   = record.get('blocked', None)
            if not blocked:
                blocked = "-"
            else:
                blocked = time_utils.datetime_to_compactdate(blocked)
                
            finished = record.get('finished', None)
            if not finished:
                finished = "-"
            else:
                finished = time_utils.datetime_to_compactdate(finished)
                
            if finished == '-':
                active_data += template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17))
            else:
                finish_data += template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17))
            
           
        print("%s\n%s" %(active_data, finish_data) )
        
        
    
    def reset_screen(self):
        """
           Do nothing
        """
        pass
    
    

    def old_print_table(self, a_db):
        """
          print a table
        """
        header_l = "------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        header   = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |"
        template = "%s|%s|%s|%s|%s|%s|%s|"
        
        print(header)
        
        for record in a_db:
            
            #reduce filename and jobname size to 50
            filename = record['filename']
            if filename:
                filename = os.path.basename(filename)
                
                #will not fail if name < 50
                filename = filename[:50]
            else:
                filename = "-"
            
            jobname = record['jobname']
            if jobname:
                #will not fail if name < 20
                jobelems = jobname.split('-')
                jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
            else:
                jobname = "-"
            
            uplinked = record.get('uplinked', None)
            if not uplinked:
                uplinked = "-"
            else:
                uplinked = time_utils.datetime_to_compactdate(uplinked)
                
            queued   = record.get('queued', None)
            if not queued:
                queued = "-"
            else:
                queued = time_utils.datetime_to_compactdate(queued)
            
            annouc   = record.get('announced', None)
            if not annouc:
                annouc = "-"
            else:
                annouc = time_utils.datetime_to_compactdate(annouc)
                
            blocked   = record.get('blocked', None)
            if not blocked:
                blocked = "-"
            else:
                blocked = time_utils.datetime_to_compactdate(blocked)
                
            finished = record.get('finished', None)
            if not finished:
                finished = "-"
            else:
                finished = time_utils.datetime_to_compactdate(finished)
            
            print(template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17)))
        
        print(header_l)
    
    
#regular expression to read aggregated info
process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 
expr_re = re.compile(process_expr)

def get_dwd_record(db, result, dirmon_dir):
    """
       Manage the particular case of DWD records
    """  
    #define type dirmon_dir -> ftp user
    if dirmon_dir == 'wmo-ra6':
        type = 'wmora6'
    else:
        type = 'dwd'
    
    records = db(filename = result['file'])
    
    for rec in records:
        if rec['metadata'].get('ftp_user') == type:
            return [rec]
    
    return []


# global to the module
s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
x_parser = xferlog_parser.XferlogParser()
d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
mapper = {'xferlog'   : 'xferlog',
          'send.log'  : 'tc-send',
          'dirmon.log' : 'dirmon'}

def remove_expired_records(db):
    """
       remove records that have been finished for more than 60 seconds
    """
    expiry_time = 60 #in seconds
    now = datetime.datetime.now()
    
    for rec in [ r for r in db if ( r.get('finished_time_insert', None) and (now - r['finished_time_insert']) > datetime.timedelta(seconds=expiry_time) )]:
        #LOG.info("rec = %s\n" %(rec))
        db.delete(rec)
    

def analyze(db, line, filename):
    """
       Analysis from the line and filename
    """
    
    the_type = mapper[filename]
            
    if the_type == 'xferlog':
        result = x_parser.parse_one_line(line)
        
        #add file in db
        db.insert(filename = result['file'],uplinked = result['time'], metadata = result['metadata'])
        
    elif the_type == 'dirmon':
        result = d_parser.parse_one_line(line)
        
        if result.get('job_status', None) == 'created':
            
            dirmon_dir = result['metadata']['dirmon_dir']
            #special case for DWD (should hopefully disappear in the future
            if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
                records = get_dwd_record(db, result, dirmon_dir)
                            
            else:       
            
                records = db(filename = result['file'])
                
            if len(records) == 0:
                #no file created so it means that the xferlog message has not been received
                # add it in the table
                db.insert(filename=result['file'], jobname = result['job'], queued = result['time'], metadata = result['metadata'])
            else:
                for rec in records:
                                                                                
                    r_job = db(jobname = result['job'])
                    
                    #if job reconcile both info
                    if r_job:
                        
                        #update filename info
                        db.update(rec, queued = result['time'], jobname = r_job[0]['jobname'], announced = r_job[0]['announced'], finished = r_job[0]['finished'])  
                        
                        #delete job record
                        db.delete(r_job[0])
                        
                    else:
                        #no other record with job name, update record
                        db.update(rec, jobname = result['job'], queued = result['time'])                
            
    elif the_type == 'tc-send':
        result = s_parser.parse_one_line(line)
        
        # look for job_status == job_announced
        if result.get('job_status') == 'announced':
            
            # get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # add a line in the to print table
                db.insert(jobname = result.get('job', None), announced = result['time'])
            else:
                for rec in records:
                    #found a job so update this line in db
                    db.update(rec, jobname = result.get('job', None), announced = result['time']) 
                   
        elif result.get('job_status') == 'blocked':
            
            #get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                db.insert(jobname = result.get('job', None), blocked = result['time'])
            else:
                for rec in records:
                    # update info with finished time
                    db.update(rec, blocked = result['time']) 
        elif result.get('job_status') == 'finished':

            #get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                db.insert(jobname = result.get('job', None), finished = result['time'], finished_time_insert = datetime.datetime.now())
            else:
                for rec in records:
                    # update info with finished time
                    db.update(rec, finished = result['time'], finished_time_insert = datetime.datetime.now())   
                    
def print_on_display(a_db, a_display, a_last_time_display):
    """
       Display every x seconds
    """ 
    if not a_last_time_display:
        a_display.print_screen(a_db)
        return datetime.datetime.now()
    else:
        current_time = datetime.datetime.now()
        if current_time - a_last_time_display > datetime.timedelta(seconds=1):
            a_display.print_screen(a_db)
            return datetime.datetime.now()
        else:
            return a_last_time_display
    
def analyze_from_tailed_file():
    """
       Analyze from an aggregated file containing xferlog, dirmon.log and send.log
    """
    agregfile = open('/tmp/logfile.log', 'r')
    
    iter = multitail.MultiFileTailer.tail([agregfile])
    
    # create database
    db = mem_db.Base('analysis')
    # create new base with field names (set mode = open) to overwrite db on next run
    #keep X elements max in collections
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', 'finished_time_insert', mode = 'open', capped_size=1000000)
    
    #display = TextDisplay()
    display = CurseDisplay()
    
    last_time_display = None
    
    try:
    
        for (f_line, _) in iter:
            
            #process only tuples (other lines should be ignored)
            matched = expr_re.match(f_line)
            if matched:
                 
                line     = matched.group('line')
                filename = matched.group('filename')
                
                analyze(db, line, filename)
                
                last_time_display = print_on_display(db, display, last_time_display)
                
                input = display.check_for_input()
                if input and input == 'QUIT':
                    break # quit loop
                
                remove_expired_records(db)
                    
        else:
            #force update
            print_on_display(db, display, None)
        
        LOG.info("Out of loop")
                
                
    except KeyboardInterrupt:
        
        #CTRL^C pressed so silently quit
        sys.exit(0)
    except Exception, e:
        
        LOG.error("In Error")
        
        error_str = utils.get_exception_traceback()
        
        LOG.error("received error %s. Traceback = %s" %(e,error_str))
    finally:
        #whatever the case always reset the screen
        display.reset_screen()
        
        print("Exiting program")
 
def analyze_from_aggregated_file():
    """
       Analyze from an aggregated file containing xferlog, dirmon.log and send.log
    """
    iter = open('/tmp/logfile.log', 'r')
    
    # create database
    db = mem_db.Base('analysis')
    # create new base with field names (set mode = open) to overwrite db on next run
    #keep X elements max in collections
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', 'finished_time_insert', mode = 'open', capped_size=1000000)
    
    #display = TextDisplay()
    display = CurseDisplay()
    
    last_time_display = None
    
    try:
    
        for elem in iter:
            #process only tuples (other lines should be ignored)
            matched = expr_re.match(elem)
            if matched:
                 
                line     = matched.group('line')
                filename = matched.group('filename')
                
                analyze(db, line, filename)
                
                last_time_display = print_on_display(db, display, last_time_display)
                
                input = display.check_for_input()
                if input and input == 'QUIT':
                    break # quit loop
                
                remove_expired_records(db)
                    
        else:
            #force update
            print_on_display(db, display, None)
        
        LOG.info("Out of loop")
                
                
    except KeyboardInterrupt:
        
        #CTRL^C pressed so silently quit
        sys.exit(0)
    except Exception, e:
        
        LOG.error("In Error")
        
        error_str = utils.get_exception_traceback()
        
        LOG.error("received error %s. Traceback = %s" %(e,error_str))
    finally:
        #whatever the case always reset the screen
        display.reset_screen()
        
        print("Exiting program")
        
         
        
def analyze_from_multiple_files():
    """
       Analyze
    """
    file_send    = open('/tmp/send.log')
    file_xferlog = open('/tmp/xferlog')
    file_dirmon  = open('/tmp/dirmon.log')
    
    iter = multitail.MultiFileTailer.tail([file_send, file_xferlog, file_dirmon])
    
    # create database
    db = mem_db.Base('analysis')
     # create new base with field names (set mode = open) to overwrite db on next run
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', mode = 'open')
    
    for (line, filename) in iter:
        
        analyze(db, line, filename)
    
    
if __name__ == '__main__': 
    
    log_utils.LoggerFactory.setup_simple_file_handler('/tmp/analyze.log') 
    
    LOG = log_utils.LoggerFactory.get_logger('ALogger')
    
    LOG.info("start")
     
    #analyze_from_aggregated_file()
    analyze_from_tailed_file()