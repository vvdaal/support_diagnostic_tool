#!/usr/bin/env python
# -*- coding: utf-8 -*-

__app_name__ = 'Telnet Diagnostic Tool'
__author__ = 'Vincent van Daal'
__author_website__ = 'http://www.vincentvandaal.nl'
__license__ = 'This work is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License. (http://creativecommons.org/licenses/by-sa/3.0/)'

#
# Telnet Diagnostic Tool
#
# Automates making a log with results from Telnet
# It checks some default URL's to actually compare the results
#
# Made by Vincent van Daal
#

#
# Load telnet library
#

import telnetlib, logging

# Create logger
logger = logging.getLogger('TELNET')
logger.setLevel(logging.DEBUG)

# Create file handler (FH) which logs even debug messages
fh = logging.FileHandler('telnet_log.log')
fh.setLevel(logging.DEBUG)

# Create console handler (CH) and set level to desired level (default INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info ('---------------------------')
logger.info ('Telnet Diagnostic Tool')
logger.info ('Version 0.1 a')
logger.info ('---------------------------')

userInput = input('Enter domain name to check (without http://, example: www.google.nl): ');

ExternalTestURLs = ['www.google.com']

ExternalTestURLs.append(userInput)
logger.debug('User entered %s as userInpit' % (userInput))

logger.debug('Going to check the following URLs: %s' % (', '.join(map(str,ExternalTestURLs))))

logger.info ('Starting diagnosing with telnet...')

for url in ExternalTestURLs:
    logger.info ('Beginning telnet of %s' % (url))

    tn = telnetlib.Telnet(url, 80, 2000)

    gethtml = "HEAD / HTTP/1.1\nHost: %s\nConnection: Close\n\n" % (url)
    logger.debug ('Executing following command through tn.write: '+ gethtml)
    tn.write(gethtml.encode('ascii'))

    logger.info (tn.read_all().decode('ascii'))

    logger.debug ('Closing telnet with tn.close()')
    tn.close()
    logger.info ('Ending telnet of %s' % (url))

logger.info ('End of diagnosing with telnet.')

logger.info ('---------------------------')
logger.info ('Finished')
logger.info ('telnet_log.log contains all logging, the file is located in the same directory as this program.')
logger.info ('---------------------------')