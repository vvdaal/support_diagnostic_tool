#!/usr/bin/env python
# coding: utf-8

#
# Tested with Python 3.3.2
#

#
# Copyright (c) 2013 Vincent van Daal
# http://www.vincentvandaal.nl
# https://github.com/VincentvDaal/support_diagnostic_tool
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


__app_name__ = 'Support Diagnostic Tool'
__app_version__ = 'V1.0.1-A'

__log_filename__ = 'diagnostics.log'


#
# Load telnet library
#

import telnetlib
import logging
import sys
import subprocess
import configparser

Config = configparser.ConfigParser()
Config.read("config.ini")

#
# Create logger
#
logger = logging.getLogger('SDT')
logger.setLevel(logging.DEBUG)

#
# Create file handler (FH) which logs even debug messages
#
fh = logging.FileHandler(__log_filename__)
fh.setLevel(logging.DEBUG)

#
# Create console handler (CH) and set level to INFO
#
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

#
# Create formatter
#
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

#
# Add the handlers to the logger
#
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == "__main__":
    logger.info ('------------------------------------------------------')
    logger.info (__app_name__ + " " +__app_version__)
    logger.info ('------------------------------------------------------')

    ExternalTestURLs = Config.get('settings', 'ExternalTestURLs').split(',')

    if Config.get('settings', 'useUserInput') == 'true' or  Config.get('settings', 'UseExternalTestURLs') == 'false':
        logger.debug('Found useUserInput to be true, asking user for input.')
        userInput = input('Type the URL to check (full domain url without http://) example: www.google.com : ')
        ExternalTestURLs.append(userInput)
        logger.debug('User entered %s as userInput' % (userInput))
    else:
        logger.debug('useUserInput is false, not asking user for input.')
    logger.debug('Going to check the following URLs: %s' % (', '.join(map(str,ExternalTestURLs))))

    logger.info ('Starting diagnostics...')
    logger.info ('Please wait until the programs states that it has completed all checks this can take a few minutes.')

    for url in ExternalTestURLs:
        # TODO-me Implement MinimumUserInfo.
        logger.info ('Beginning telnet to %s' % (url))

        try:
            tn = telnetlib.Telnet(url, 80, 2000)

            #
            # We will use a HEAD / HTTP1.1 command through Telnet to fetch the result.
            # This should give more than enough debugging information since it will the responding HTTP status code.
            #
            gethtml = "HEAD / HTTP/1.1\nHost: %s\nConnection: Close\n\n" % (url)

            logger.debug ('Executing following command through tn.write: '+ gethtml)
            tn.write(gethtml.encode('ascii'))

            logger.info (tn.read_all().decode('ascii'))

            logger.debug ('Closing telnet with tn.close()')
            tn.close()

        except:
            logger.info ('Telnet returned an error, the error has been logged.')
            logger.debug ('Telnet error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending telnet to %s' % (url))

        logger.info ('Beginning traceroute to %s' % (url))

        try:

            #
            # Because Windows uses "tracert" instead of "traceroute" we have to check first what OS we are running the script on.
            #
            if(sys.platform.startswith('win')): # Using Windows
                command = ["tracert", '-d', '-w', '1000', url]
            else: # Using other than Windows
                command = ["traceroute", '-n', '-w', '1000', url]

            ef = subprocess.check_output(command, shell=False, stderr=None)

            logger.info(ef.decode('ASCII'))
        except:
            logger.info ('tracert returned an error, the error has been logged.')
            logger.debug ('tracert error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending traceroute to %s' % (url))

        logger.info ('Beginning nslookup for %s' % (url))
        try:
            #
            # NSlookup tool should work the same in every OS.
            #
            ef = subprocess.check_output(["nslookup", url], shell=False, stderr=None)

            logger.info(ef.decode('ASCII'))
        except:
            logger.info ('NSlookup returned an error, the error has been logged.')
            logger.debug ('NSlookup error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending nslookup for %s' % (url))

    logger.info ('------------------------------------------------------')
    logger.info ('Completed all checks - Finished diagnosing')
    logger.info ('')
    logger.info ('%s contains all logging, this file is located in the same directory as this program.' % (__log_filename__))
    logger.info ('------------------------------------------------------')

    input() # Ensure the Window doesn't close immediately.