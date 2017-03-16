#!/usr/bin/env python

'''Functions to download the large .nc files and store them onsite in a directory tree. Multiprocessing enabled'''

from datetime import datetime, timedelta
import os
from multiprocessing.dummy import Pool # use threads for I/O bound tasks
from urllib.request import urlretrieve
import requests
import sys

#return yesterday's date in yyyymmdd form
def getYesterdate():
    #get yesterday's date
    return datetime.strftime(datetime.now() - timedelta(2), '%Y%m%d')
    

#numbers go from 0001 (1am utc) to 0073 (midnight 2 days later)
#returns the hour string part of the url
def getHourString( hour ):
    if not isinstance(hour, int):
        raise ValueError('Argument "hour" must be an int.' )

    if (hour < 2) or (73 < hour):
        raise ValueError('Argument "hour" must be an int > 1 and < 74.' )
    else:
        #pad out with leading 0's
        hour = str(hour).zfill( 4 ) 
        base = 'ocean_his_{}.nc'
        return base.format( hour )

#get the list of urls corresponding to yetsterday's forcast
def getYesterdayURLs():
    
    urls = [None] * 72
    
    #yyyymmdd string
    date = getYesterdate()
    
    #example url
    #https://pm2.blob.core.windows.net/f20160608/ocean_his_0002.nc
    url = "https://pm2.blob.core.windows.net/f{}/{}"
    
    for i in range(0, 72):
        #urls[i] = url.format( date, getHourString(i + 1))
        urls[i] = ( url, date, getHourString(i + 2) )
    
    return urls

#input a string path to a file
#ensure the containing folder exists
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
# download a file     
def downloadFile( url ):
     
    final_filename = 'ncFiles/{}/{}'.format( url[1], url[2])
    local_filename = final_filename.replace('.nc', ".temp")
    
    #convert tuple to a string to build the url
    url = url[0].format( url[1], url[2] )
    
    
    # NOTE the stream=True parameter
    response = requests.get(url, stream=True)
    
    length = response.headers.get('content-length')
    
    
    with open(local_filename, 'wb') as f:
        if length is None:
            f.write( response.content )
        else:
            dl = 0
            length = int( length )
            for chunk in response.iter_content(chunk_size=1024):
                   
                if chunk: # filter out keep-alive new chunks
                    dl += len( chunk )
    
                    #write the chunk
                    f.write(chunk)
                    
                    #command line progress bar
                    done = int(50 * (dl / length) )
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
         
               
    #create an empty file at the final destination    
    final = open( final_filename, 'w' )
    final.close()
    
    #move the file once it is done
    os.rename( local_filename, final_filename )
                    
    return local_filename


    
def downloadYesterday():
    
    urls = getYesterdayURLs()
    
    #check if an item already exists (already downloaded)
    def itemNotDownloaded( item ):
        if os.path.isfile(  "ncFiles/{}/{}".format( item[1], item[2] ) ):
            return False
        return True
    
    #filter out the files which already exists and don't need to be downloaded
    urls = list(filter( itemNotDownloaded, urls ))
    
    date = getYesterdate()
    
    ensure_dir( "ncFiles/{}/test.txt".format(date) )
    
    #creates a pool of n processes where n is cpu count
    #maps the indexes in urls to processes
    result = Pool().map(downloadFile, urls) # download 4 files at a time
            
downloadYesterday()

    

    