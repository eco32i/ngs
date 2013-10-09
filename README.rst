CuffBase
========

A Django project that takes the output of the _tophat/cufflinks pipeline: http://tophat.cbcb.umd.edu/, builds
an SQL database (by default MySQL) in much the same way _cummeRbund: http://compbio.mit.edu/cummeRbund/ does
and makes it available through the Web interface. Unlike cummeRbund, 
multiple pipeline runs can be stored in the same database.

The primary goal of CuffBase is to make the results of cuffdiff pipeline
accessible for a bench scientist.

Provides _very limited_ plotting facilities via matplotlib.

Dependencies
=============

* _django: http://www.djangoproject.com/
* _django-pagination: https://pypi.python.org/pypi/django-pagination
* _matplotlib: http://matplotlib.org/
* _brewer2mpl: https://github.com/jiffyclub/brewer2mpl.git
* _pandas (used in plot generation): http://pandas.pydata.org/pandas-docs/stable/
* _gunicorn: http://gunicorn.org -- for easy deployment
* data from the tophat/cufflinks pipeline (bunch of tab-delimited text files)

Deployment
===========

The recommended way to deploy CuffBase is to setup Apache2 or Gunicorn
behind Nginx server.

Qiuck start
============
You need to set up your database and specify relevant information (backend,
username, and password) in the ngs/settings.py file before trying to
import cuffdiff output results. For example, if using MySQL:

    mysql> create database <database-name> default charset utf8 collate utf8_general_ci;
    mysql> grant all on <database-name>.* to <user>@localhost identified by <password>;
    
and then the databases section of your ``ngs/settings.py`` file should read:
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '<database-name>',
            'USER': '<user>',
            'PASSWORD': '<password>',
            'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',                      # Set to empty string for default.
        }
    }

to load the example database from the provided sql dump:

    $ gunzip -c ngs-dump-1.gz | mysql -u<user> -p<password> <database-name>

to import the cuffdiff output run this from the cuffbase directory:

    $ ./manage.py import_exp <path-to-cuffdiff-output>

to start development server locally run this from the cuffbase directory:

    $ ./manage.py runserver --insecure

and cuffbase should be accessible in your browser at ``http://localhost:8080/cuff``

Caveats and limitations
=======================
I did my best trying to stick as close to the original cummeRbund
database schema as possible. I had, however, to use integer pks instead
of string pks in cummeRbund to make it play nicely with Django ORM. In 
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
* port to Python 3 (should be easy?)
* IPython notebook integration?

