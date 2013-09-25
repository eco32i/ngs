CuffBase
========

A Django app that takes the output of the _tophat/cufflinks pipeline: http://tophat.cbcb.umd.edu/, builds
an SQL database (by default MySQL) in much the same way _cummeRbund: http://compbio.mit.edu/cummeRbund/ does
and makes it available through the Web interface. Unlike cummeRbund, 
multiple runs can be stored in the same database.

The primary goal of CuffBase is to make the results of cuffdiff pipeline
accessible for a bench scientist.

Provides rudimentary plotting facilities via matplotlib.

Dependencies
=============

* _django: http://www.djangoproject.com/
* _django-pagination: https://pypi.python.org/pypi/django-pagination
* _matplotlib: http://matplotlib.org/
* _pandas (used in plot generation): http://pandas.pydata.org/pandas-docs/stable/
* _gunicorn: http://gunicorn.org -- for easy deployment
* data from the tophat/cufflinks pipeline (bunch of text files)

Deployment
===========

The recommended way to deploy CuffBase is to setup Apache2 or Gunicorn
behind Nginx server.

Caveats and limitations
=======================
I did my best trying to stick as close to the original cummeRbund
database schema as possible. I had, however, to use integer pks instead
of string pks in cummeRbund to make it play nicely with Django. In 
addition, PhenoData, Feature, and Attribute tables are basically
placeholders. Not sure what to make of them.

* no tests -- the project was concieved as an ad-hoc solution with little
consideration for future maintenance (I wasn't sure it'd work at all!)
* tests are sorely needed -- will be the first priority in moving forward
* no docs -- same as the tests
* not tested with anything but MySQL 5.5
* it was only tested on full cuffdiff output

Future plans
============

* interactive plotting with Bokeh
* tests
* docs (mostly on deployment)
* IPython notebook integration?

