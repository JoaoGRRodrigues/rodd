'''
Created on Dec 1, 2011

@author: guillaume.aubert@gmail.com
'''
import os

import datetime
import calendar

def get_ym_from_datetime(a_datetime):
    """
       return year month from datetime
    """
    if a_datetime:
        return a_datetime.strftime('%Y-%m')
    
    return None

MONTH_CONV = { 1: 'Jan', 4: 'Apr', 6: 'Jun', 7: 'Jul', 10: 'Oct' , 12: 'Dec',
               2: 'Feb', 5: 'May', 8: 'Aug', 9: 'Sep', 11: 'Nov',
               3: 'Mar'}

def datetime2imapdate(a_datetime):
    """
       Transfrom in date format for IMAP Request
    """
    if a_datetime:
        
        month = MONTH_CONV[a_datetime.month]
        
        pattern = '%%d-%s-%%Y' %(month) 
        
        return a_datetime.strftime(pattern)
    

def e2datetime(a_epoch):
    """
        convert epoch time in datetime

            Args:
               a_epoch: the epoch time to convert

            Returns: a datetime
    """

    #utcfromtimestamp is not working properly with a decimals.
    # use floor to create the datetime
#    decim = decimal.Decimal('%s' % (a_epoch)).quantize(decimal.Decimal('.001'), rounding=decimal.ROUND_DOWN)

    new_date = datetime.datetime.utcfromtimestamp(a_epoch)

    return new_date

def datetime2e(a_date):
    """
        convert datetime in epoch
        Beware the datetime as to be in UTC otherwise you might have some surprises
            Args:
               a_date: the datertime to convert

            Returns: a epoch time
    """
    return calendar.timegm(a_date.timetuple())

def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)

def __rmgeneric(path, __func__):
    """ private function that is part of delete_all_under """
    try:
        __func__(path)
        #print 'Removed ', path
    except OSError, (errno, strerror): #IGNORE:W0612
        print """Error removing %(path)s, %(error)s """%{'path' : path, 'error': strerror }
            
def delete_all_under(path,delete_top_dir=False):
    """ delete all files and directories under path """

    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            __rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            delete_all_under(fullpath)
            f=os.rmdir
            __rmgeneric(fullpath, f)
    
    if delete_top_dir:
        os.rmdir(path)