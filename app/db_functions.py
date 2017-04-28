
"""Functions to handle creation, population, and access of sqlite database."""

import os
import sys
from app import app, views, compress_functions, netcdf_functions
from sqlite3 import dbapi2 as sqlite3
import netCDF4 as nc
import json
from json import encoder
from flask_redis import FlaskRedis

app.config.update(dict(
    REDIS_URL="redis://localhost:6379/0"
))

redis_store = FlaskRedis(app, decode_responses=False)

compressData = compress_functions.compressData


def connect_db():
    """Connects to the specific database."""
    #rv = sqlite3.connect(app.config['DATABASE'])
    #rv.row_factory = sqlite3.Row
    return redis_store

def setcwd(path):
    '''set the current working directory to the path'''    
    os.chdir(path)

def init_db():
    """Initializes the database"""
    db = get_db()

def get_all_entries():
    db = get_db()
    out = {}
    for key in db.keys():
        out[key] = db.get(key)
        
    return out
def get_keys():
    db = get_db()
    return db.keys()

def populate_db():
    """Populate the db with data from the 'ncfiles' folder"""
    db = get_db()
    ncFilesDir = "./app/ncFiles/"
    
    #control precision of floats when they are jsonified
    #http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module/1447581
    c_make_encoder = encoder.c_make_encoder
    encoder.c_make_encoder = None
    original = encoder.FLOAT_REPR
    encoder.FLOAT_REPR = lambda o: format(o, '.2f')
    
    #put the data in rows
    for root, dirs, files in os.walk(ncFilesDir, topdown=False):
        for name in dirs:
            yearString = name
            yearPath = ncFilesDir + name
            for root, dirs, files in os.walk( yearPath ):
                first = True
                frames = []
                for name in files:
                    
                    #get the top level of salt data in the file
                    fn = yearPath + "/" + name
                    salt = netcdf_functions.getData(40, 39, fn )
                                        
                    if ( salt != None ):
                        date = yearString + name [ -5:-3 ]
                        
                        frame = {}
                        if(first):
                            first = False
                            axisData = netcdf_functions.getAxisData(fn)
                            #db.execute("insert into entries (date, z, ratio, lon, lat) values (?, ?, ?, ?, ?)", [date, saltJSON, json.dumps(axisData['ratio']), json.dumps(axisData['lon']), json.dumps(axisData['lat'])] )
                            frame.update({"ratio":axisData['ratio'], "lon":axisData['lon'], "lat":axisData['lat']})
                                        
                        #add in the z data                
                        frame.update({"yyyymmddhh":date, "z":salt})
                        frames.append(frame)

                #commit the frames both as compressed and not compressed, in json format
                db.set("frames", json.dumps(frames))
                db.set("framesCompressed", compressData(json.dumps(frames).encode('utf-8')))
    
    
    #set back to original
    encoder.FLOAT_REPR = original
    encoder.c_make_encoder = c_make_encoder

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    populate_db()
    
@app.cli.command('printrowcount')
def printrowcount_command():
    """Print the database."""
    entries = get_all_entries()
    print( "entry count: \n" + str( len(entries)) )
    
@app.cli.command('printdb')
def printdb_command():
    """Print the database."""
    entries = get_all_entries()
    print( "entries: \n" + str( entries) )


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    return redis_store

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""

        
def getCompressedTable():
    """Get the precompressed data"""
    db = get_db()
    
    return db.get("framesCompressed")
    
def getTableAsJson(table="entries"):
    """Get the specified table as a jsoned list of jsoned rows"""
    db = get_db()
    return db.get("frames")

