'''

The presence of "//" within a URL's path is an indicator that may suggest redirection to an external website. The expected position of "//" in a URL is determined by the protocol it uses. 
For URLs beginning with "HTTP," "//" is anticipated to be located at the sixth position, whereas for "HTTPS" URLs, it should be found at the seventh position.
If "//" appears in any location other than immediately following the protocol, this characteristic is evaluated for security purposes. 
Specifically, a value of 1 (indicating a phishing attempt) is assigned if "//" is found outside its expected position. 
Conversely, a value of 0 is assigned to signify a legitimate URL, reflecting that the "//" is appropriately placed directly after the protocol.

'''

# 6.Checking for redirection '//' in the url (Redirection)
def redirection(url):
    pos = url.rfind('//')
    if pos > 6:
        if pos > 7:
            return 1
        else:
            return 0
    else:
        return 0
