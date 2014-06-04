import qErr


def downloadFile(file_name, base_url, timeout=20, binary=False, verbose=False):
    '''
    file_name: string of desired file name after download. e.g. 'download.png'
    base_url: URL of desired file
    timeout: how long to wait (seconds) before giving up
    binary: open file in binary mode (as opposed to text mode)  
    verbose: list each file downloading in the prompt
    '''
    from urllib2 import Request, urlopen, URLError, HTTPError
    
    #create the url and the request
    url = base_url + file_name
    req = Request(url)
    successful_download = False
    count = 0

    # distinguish as binary file if desired
    file_mode = ''
    if binary:
        file_mode = 'b'
    
    # Open the url:
    while not successful_download and count < 6:
        count += 1
        trys_left = 5-count
        try:
            f = urlopen(req, timeout=timeout)
            if verbose: 
                print "downloading " + url

            # Open our local file for writing
            local_file = open(file_name, "w" + file_mode)
            #Write to our local file
            local_file.write(f.read())
            local_file.close()
            successful_download = True

        #handle errors
        except HTTPError, e:
            print "HTTP Error:",e.code , url
            print "Trying again: %i attempts remaining" % (trys_left+1)
            if trys_left <= -1: qErr.qErr()
        except URLError, e:
            print "URL Error:",e.reason , url
            print "Trying again: %i attempts remaining" % (trys_left+1)
            if trys_left <= -1: qErr.qErr()
        except:
            print "Couldn't Download for unknown reasons!"
            print "Trying again: %i attempts remaining" % (trys_left+1)
            if trys_left <= -1: qErr.qErr()

def downloadImage(img_url, out_name=None, timeout=20):
    '''Wrapper for image downloads
    '''
    if not out_name:
        try:
            out_name = img_url.split('/')[-1]
        except:
            out_name = 'qImage.jpg'
    downloadFile(out_name,img_url, timeout=timeout,binary=True)