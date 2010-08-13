'''
Created on Aug 13, 2010

@author: guillaume.aubert@eumetsat.int
'''

import xml.dom.minidom
import xpath


def run_test():
        doc = xml.dom.minidom.parse('/homespace/gaubert/RODD/src-data/130810-vprodnav/3.xml').documentElement
        
        # create context
        context = xpath.XPathContext()
        
        c = { 'gmi': "http://www.isotc211.org/2005/gmi",
              'eum': "http://www.eumetsat.int/2008/gmi",
              'gco': "http://www.isotc211.org/2005/gco",
              'gmd': "http://www.isotc211.org/2005/gmd",
              "xsi": "http://www.w3.org/2001/XMLSchema-instance"
            }
        
        context.namespaces['gmi'] = "http://www.isotc211.org/2005/gmi"
        context.namespaces['eum'] = "http://www.eumetsat.int/2008/gmi"
        context.namespaces['gco'] = "http://www.isotc211.org/2005/gco"
        context.namespaces['gmd'] = "http://www.isotc211.org/2005/gmd"
        context.namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        

        
        #result = xpath.find('gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=c)
        result = xpath.find('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString/text()', doc, namespaces=c)
        print("Result = %s\n" % (result))
        
        result = context.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=c)
        print("Result = %s\n" % (result))



if __name__ == '__main__':
    run_test()