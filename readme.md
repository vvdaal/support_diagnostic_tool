Support Diagnostic Tool
=======================

This tool offers an easier way to troubleshoot network related issues. It has "Customer Ease" in mind and allows customers without much knowledge
to just run this tool in a "Fire and Forget" way and make a log of all results which will then require a analyses by a more knowledgeable person.

It checks a domain together with some default much visited domains to debug network related issues such as but not limited to:
See if a website gets blocked due to a specific protocol Firewall
See if a website gets blocked due to a regular Firewall
See if a website doesn't work due to DNS issues or Proxy usage

In short this tool should allow you great insight if people are having issues reaching their domain or services in regards to their domain.
This tool is originally made for and also used by a major dutch Webhosting Company.

Changelog release V1.0.2 (Hotfix)
* Hotfix for ensuring compatibility with 32bit systems.
* Changed Windows executable to use Python 2.7 instead of Python 3.3

Changelog release V1.0.1

* More configuration options.
* Possibility to get external IP.
* Improved Popen handling
* Overall performance improvement
* Added second nslookup through Google DNS by default to troubleshoot DNS related problems.
* Made both Python 2 and Python 3 scripts available, the Windows binary makes use of the Python 3 Library.