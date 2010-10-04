'''
Created on Sep 29, 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy
import decimal
import simplejson as json

from sqlalchemy.orm import mapper, relationship, backref
from eumetsat.db import connections


class Product(object):
    """ Product Object """
    def __init__(self, title, internal_id, description, disseminated, status):
        self.rodd_id            = None
        self.title              = title
        self.internal_id        = internal_id
        self.description        = description
        self.is_disseminated    = disseminated
        self.status             = status
        self.data_centre_infos  = []
        self.gts_infos          = []
        self.eumetcast_infos    = []
        self.geonetcast_infos   = []
  
    def __repr__(self):
        return "<Product(%s'%s', '%s', '%s', '%s', '%s', files= [ eumetcast = ('%s'), gts = ('%s'), data_centre= ('%s'), geonetcast = ('%s') )>" \
               % ( (( "'rodd_id:%s', " % (self.rodd_id)) if self.rodd_id else ""), \
                     self.title, self.internal_id, \
                     self.description ,\
                     self.is_disseminated, \
                     self.status, \
                     self.eumetcast_infos, \
                     self.gts_infos, \
                     self.data_centre_infos, \
                     self.geonetcast_infos)
    
    def jsonize(self):
        
        result = {}
        
        result["name"]         = self.title 
        result["uid"]          = self.internal_id
        result["description"]  = self.description
        result["distribution"] = []
        
        
        result["eumetcast-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "eumetcast-info" not in result["distribution"]:
                result["distribution"].append("eumetcast-info")
            
            result["eumetcast-info"]["files"].append(finfo.jsonize())
            
        
        result["gts-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "gts-info" not in result["distribution"]:
                result["distribution"].append("gts-info")
            
            result["gts-info"]["files"].append(finfo.jsonize())
        
        result["data-centre-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "data-centre-info" not in result["distribution"]:
                result["distribution"].append("data-centre-info")
            
            result["data-centre-info"]["files"].append(finfo.jsonize())
       
        result["geonetcast-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "geonetcast-info" not in result["distribution"]:
                result["distribution"].append("geonetcast-info")
            
            result["geonetcast-info"]["files"].append(finfo.jsonize())
            
            
        return result
        
class ServiceDir(object):
    """ServiceDir object """
    def __init__(self, name, channel):
        self.serv_id     = None
        self.name        = name
        self.channel     = channel
    
    def __repr__(self):
        return "<ServiceDir(%s'%s', '%s')>" % ( (("'serv_id:%s', " % (self.serv_id)) if self.serv_id else ""),\
                                                self.name, \
                                                self.channel)
    
    def jsonize(self):
        """ jsonize """
        result = {}
        
        result['name']    = self.name
        result['channel'] = self.channel.name if self.channel else "" 
        
        return result
    
class DistributionType(object):
    """ DistributionType object """
    def __init__(self, name):
        self.name     = name
    
    def __repr__(self):
        return "<DistributionType('%s')>" % (self.name)
    
class Channel(object):
    """ Channel object """
    
    def __init__(self, name, address, min_rate, max_rate, channel_function):
        """ constructor """
        self.chan_id           = None
        self.name              = name
        self.multicast_address = address
        self.min_rate          = min_rate
        self.max_rate          = max_rate
        self.channel_function  = channel_function
        
    def __repr__(self):
        return "<Channel(%s'%s', '%s', '%s', '%s', '%s')>" % ( (( "'chan_id:%s', " % (self.chan_id)) if self.chan_id else ""),\
                                                              self.name, self.multicast_address, self.min_rate, self.max_rate, self.channel_function)
    
    def jsonize(self):
        """ jsonize """
        result = {}
        
        result['name']              = self.name
        result['multicast_address'] = self.multicast_address
        
        # given as decimal by sqlalchemy to ROUND_UP to get only integer values 
        result['min_rate']            = str(decimal.Decimal(self.min_rate).quantize(decimal.Decimal('1')))
        result['max_rate']            = str(decimal.Decimal(self.max_rate).quantize(decimal.Decimal('1')))
        
        result['channel_function']    = self.channel_function
        
        return result
        

class FileInfo(object):
    """ FileInfo object """
    def __init__(self, name, reg_expr, size, type):
         
        self.name         = name
        self.reg_expr     = reg_expr
        self.size         = size
        self.type         = type
        self.service_dirs = []
    
    def __repr__(self):
        return "<FileInfo('%s','%s', '%s', '%s', '%s')>" % (self.name, self.reg_expr, self.size, self.type, self.service_dirs)

    def jsonize(self):
        
        result = {"service_dir" : []}
        
        result["name"]        = self.name
        result["regexpr"]     = self.reg_expr
        result["size"]        = self.size
        result["type"]        = self.type
        
        for service_dir in self.service_dirs:
            result["service_dir"].append(service_dir.name)
            
        return result
        

class DAO(object):
    """ This is singleton """
    
    _instance = None
    _created   = False
    
    def __init__(self):
        
        if not DAO._created:
            self.conn     = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
            self.metadata = None
            self.tbl_dict = {}
            # load dao info
            self._load()
            
            DAO._created = True
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DAO, cls).__new__(
                                cls, *args, **kwargs)
            
        return cls._instance
 
    def _load(self):
        """ load the RODDDAO info """
        self.conn.connect()
        
        self.metadata = self.conn.get_metadata()
        
        self.tbl_dict['products']      = sqlalchemy.Table('products', self.metadata, autoload = True)
    
        # load service dirs table
        self.tbl_dict['service_dirs']  = sqlalchemy.Table('service_dirs', self.metadata, \
                                                          sqlalchemy.ForeignKeyConstraint(['chan_id'], ['channels.chan_id']), \
                                                          autoload= True)
        
        # load file_info table
        self.tbl_dict['file_info']     = sqlalchemy.Table('file_info', self.metadata, autoload= True)
        
        # load file_info table
        self.tbl_dict['channels']      = sqlalchemy.Table('channels', self.metadata, autoload= True)
        
        
        #create many to many relation table
        # beware add foreign key constraints manually as they do not exist in MYSQL
        products_2_eumetcast_table      = sqlalchemy.Table('products_2_eumetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_eumetcast'] = products_2_eumetcast_table
        
        products_2_geonetcast_table     = sqlalchemy.Table('products_2_geonetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_geonetcast'] = products_2_geonetcast_table
        
        products_2_gts_table            = sqlalchemy.Table('products_2_gts', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_gts'] = products_2_gts_table
        
        products_2_data_centre_table    = sqlalchemy.Table('products_2_data_centre', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_data_centre'] = products_2_data_centre_table
        
        file_2_servdirs_table           = sqlalchemy.Table('file_2_servdirs', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['serv_id'], ['service_dirs.serv_id']), \
                                                     autoload = True)
        
        self.tbl_dict['file_2_servdirs'] = file_2_servdirs_table
    
        # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
        mapper(Product, self.tbl_dict['products'], properties={
        'data_centre_infos'  :  relationship(FileInfo,   secondary=products_2_data_centre_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'gts_infos'          :  relationship(FileInfo,   secondary=products_2_gts_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'eumetcast_infos'    :  relationship(FileInfo  , secondary=products_2_eumetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'geonetcast_infos'   :  relationship(FileInfo  , secondary=products_2_geonetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        })
        
        # map file_info table
        mapper(FileInfo, self.tbl_dict['file_info'], properties={
        'service_dirs'   : relationship(ServiceDir, secondary=file_2_servdirs_table),
        })
        
        # map channels table
        mapper(Channel, self.tbl_dict['channels'])
        
        # one to many relationship servicedirs -> channel
        mapper(ServiceDir, self.tbl_dict['service_dirs'], properties = {
            'channel': relationship(Channel)
        })

        

    def get_table(self, name):
        """ return table from the DAO """
        return self.tbl_dict[name]
    
    def get_session(self):
        """ return the session """
        return self.conn.get_session()
    