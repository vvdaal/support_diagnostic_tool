#!/usr/bin/env python
# coding: utf-8

#
# Tested with Python 3.3.2
#

#
# Copyright (c) 2013 Vincent van Daal
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
__app_version__ = '1.0'
__log_filename__ = 'diagnostics.log'

#
# This tool offers an easier way to troubleshoot network related issues. It has "Customer Ease" in mind and allows customers without much knowledge
# to just run this tool in a "Fire and Forget" way and make a log of all results which will then require a analyses by a more knowledgeable person.
#
# It checks a domain together with some default much visited domains to debug network related issues such as but not limited to:
# See if a website gets blocked due to a specific protocol Firewall
# See if a website gets blocked due to a regular Firewall
# See if a website doesn't work due to DNS issues or Proxy usage
#
# In short this tool should allow you great insight if people are having issues reaching their domain or services in regards to their domain.
# This tool is originally made and also used by a major dutch Webhosting Company.
#
# Made by Vincent van Daal
# http://www.vincentvandaal.nl
# https://github.com/VincentvDaal/support_diagnostic_tool
#


#
# Load telnet library
#

import telnetlib, logging, sys, subprocess, configparser

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
    logger.info ('---------------------------')
    logger.info (__app_name__)
    logger.info (__app_version__)
    logger.info ('---------------------------')

    ExternalTestURLs = Config.get('settings', 'ExternalTestURLs').split(',')

    if Config.get('settings', 'useUserInput') == 'true':
        logger.debug('Found useUserInput to be true, asking user for input')
        userInput = input('Type the FQDN domain name to check (full domain name without http://) example: www.google.com: ');
        ExternalTestURLs.append(userInput)
        logger.debug('User entered %s as userInput' % (userInput))

    logger.debug('Going to check the following URLs: %s' % (', '.join(map(str,ExternalTestURLs))))

    logger.info ('Starting diagnostics...')
    logger.info ('Please wait until the programs states that it has completed all checks this can take a few minutes.')

    for url in ExternalTestURLs:
        logger.info ('Beginning telnet to %s' % (url))

        try:
            tn = telnetlib.Telnet(url, 80, 2000)

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
            ef = subprocess.check_output(["tracert", '-d', '-w', '1000', url], shell=False, stderr=None)
            logger.info(ef.decode('ASCII'))
        except:
            logger.info ('tracert returned an error, the error has been logged.')
            logger.debug ('tracert error with %s (%s)' % (url, sys.exc_info()))

        #
        # Legacy code for subprocess line-by-line reading
        #
        #while True:
        ##    line = p.stdout.readline()
        #    if not line: break
        #    output = '-->',line,
        #    logger.info(str(output).decode('ASCII')).
        #p.wait()


        logger.info ('Ending traceroute to %s' % (url))

        logger.info ('Ending telnet to %s' % (url))

        logger.info ('Beginning nslookup for %s' % (url))
        try:
            ef = subprocess.check_output(["nslookup", url], shell=False, stderr=None)
            logger.info(ef.decode('ASCII'))
        except:
            logger.info ('NSlookup returned an error, the error has been logged.')
            logger.debug ('NSlookup error with %s (%s)' % (url, sys.exc_info()))

        logger.info ('Ending nslookup for %s' % (url))

    logger.info ('---------------------------')
    logger.info ('Completed all checks - Finished diagnosing')
    logger.info ('')
    logger.info ('%s contains all logging, this file is located in the same directory as this program.' % (__log_filename__))
    logger.info ('---------------------------')