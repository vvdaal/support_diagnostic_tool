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
__app_version__ = 'V1.0.1'

__log_filename__ = 'diagnostics.log'


#
# Load telnet library
#

import telnetlib
import logging
import sys
import subprocess
import configparser
import time

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
formatter_ch = logging.Formatter('%(message)s')
formatter_fh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter_ch)
fh.setFormatter(formatter_fh)

#
# Add the handlers to the logger
#
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == "__main__":

    app_header = '------------------------------------------------------\n%s - %s\n------------------------------------------------------' % (__app_name__, __app_version__)

    logger.info(app_header)

    #
    # Try to get useUserInput from the config.ini
    #
    try:
        useUserInput = Config.get('settings', 'useUserInput')
        logger.debug('Loaded useUserInput from config file.')
    except:
        useUserInput = 'true'
        logger.warning('Could not find useUserInput in config file, using default value.')
        logger.debug ('Config.get error: %s' % (sys.exc_info()[0]))

    #
    # Try to get UseExternalTestURLs from the config.ini
    #
    try:
        UseExternalTestURLs = Config.get('settings', 'UseExternalTestURLs')
        logger.debug('Loaded UseExternalTestURLs from config file.')
    except:
        UseExternalTestURLs = 'true'
        logger.warning('Could not find UseExternalTestURLs in config file, using default value.')
        logger.debug ('Config.get error: %s' % (sys.exc_info()[0]))

    #
    # Checks if both UseExternalTestURLs and useUserInput are false
    # This is not allowed (since the program actually needs to do something)
    # It will then set useUserInput to true
    #
    if UseExternalTestURLs == 'false' and useUserInput == 'false':
        logger.debug ('Both UseExternalTestURLs and useUserInput are false, this is not allowed, using default value of true for useUserInput')
        useUserInput = 'true'

    #
    # Try to get ExternalTestURLs from the config.ini
    #
    try:
        ExternalTestURLs = Config.get('settings', 'ExternalTestURLs').split(',')
        logger.debug('Loaded ExternalTestURLs from config file.')
    except:
        ExternalTestURLs = ['google.com','facebook.com']
        logger.warning('Could not find ExternalTestURLs in config file, using default values.')
        logger.debug ('Config.get error: %s' % (sys.exc_info()[0]))

    #
    # Check if useUserInput is actually true or if UseExternalTestURLs is false or if both useUserInput and UseExternalTestURLs are false
    # Since the program needs to do something we need to build in this check
    #
    if useUserInput == 'true' or UseExternalTestURLs == 'false':
        logger.debug('Found useUserInput to be true, asking user for input.')
        userInput = input('Type the URL to check (full domain url without http://) example: www.google.com : ')
        ExternalTestURLs.append(userInput)
        logger.debug('User entered %s as userInput' % (userInput))
    else:
        logger.debug('useUserInput is false, not asking user for input.')
        
    logger.debug('Going to check the following URLs: %s' % (', '.join(map(str,ExternalTestURLs))))

    logger.info ('Starting diagnostics...')
    logger.info ('')
    logger.info ('')
    logger.info ('Please wait until the programs states that it has completed all checks this can take a few minutes.')
    logger.info ('')
    logger.info ('')
    time.sleep(1)
    #
    # Go through every url in ExternalTestURLs
    #
    for url in ExternalTestURLs:
        # TODO-me Implement MinimumUserInfo.
        logger.info ('Beginning telnet to %s' % (url))

        try:
            #
            # Open telnet to the url with port 80, 2 second timeout (2000ms)
            #
            tn = telnetlib.Telnet(url, 80, 2000)

            #
            # We will use a HEAD / HTTP1.1 command through Telnet to fetch the result.
            # This should give more than enough debugging information since it will the responding HTTP status code.
            #
            gethtml = "HEAD / HTTP/1.1\nHost: %s\nConnection: Close\n\n" % (url)

            #
            # Write the command requested through telnet to the log but do not display it to the user.
            #
            logger.debug ('Executing following command through tn.write: '+ gethtml)
            tn.write(gethtml.encode('ascii'))

            #
            # Read all responses from telnet and ensure proper decoding.
            #
            logger.info (tn.read_all().decode('ascii'))

            logger.debug ('Closing telnet with tn.close()')

            #
            # Close actual telnet connection
            #
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

            ef = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
            while True:
                line = ef.stdout.readline().decode('ASCII')
                if line != '':
                    logger.info (line.rstrip())
                else:
                    break

            #for line in iter(ef.stdout.readline,''):
            #    logger.info (line.rstrip())

            #logger.info(ef.decode('ASCII'))
        except:
            logger.info ('tracert returned an error, the error has been logged.')
            logger.debug ('tracert error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending traceroute to %s' % (url))

        logger.info ('Beginning nslookup for %s' % (url))

        try:

            #
            # NSlookup tool should work the same in every OS.
            #
            command = ["nslookup", url]

            ef = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
            while True:
                line = ef.stdout.readline().decode('ASCII')
                if line != '':
                    logger.info (line.rstrip())
                else:
                    break

        except:
            logger.info ('NSlookup returned an error, the error has been logged.')
            logger.debug ('NSlookup error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending nslookup for %s' % (url))

    logger.info ('------------------------------------------------------')
    logger.info ('Completed all checks - Finished diagnosing')
    logger.info ('')
    logger.info ('%s contains all logging, this file is located in the same directory as this program.' % (__log_filename__))
    logger.info ('')
    logger.info ('English: Send the %s file to the Support-Desk.' % (__log_filename__))
    logger.info ('Dutch: Verstuur het %s bestand naar de Support-Desk.' % (__log_filename__))
    logger.info ('German: Senden Sie die %s datei zu Support-Desk. ' % (__log_filename__))
    logger.info ('')
    logger.info ('------------------------------------------------------')

    input() # Ensure the Window doesn't close immediately.
