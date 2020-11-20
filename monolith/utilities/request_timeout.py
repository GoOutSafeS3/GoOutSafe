from datetime import datetime
import datetime
import requests

TIMEOUT = 1

def get(url):
    """ Makes a get request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def post(url,json):
    """ Makes a post request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.post(url, json=json, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def put(url,json):
    """ Makes a put request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.put(url, json=json, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def patch(url,json):
    """ Makes a patch request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.patch(url, json=json, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def delete(url):
    """ Makes a delete request with a timeout.

    Returns the json object if with the status code (or None, None in case of connection error).
    """
    try:
        r = requests.delete(url, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code   
    except:
        return None,None