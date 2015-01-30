CuffBase
========

A Django-based frontend for the persistent storage, analysis and visualization of the output of tophat/cufflinks pipeline. CuffBase takes the output of the `tophat/cufflinks pipeline <http://tophat.cbcb.umd.edu/>`_, builds an SQL database (by default MySQL) in much the same way `cummeRbund <http://compbio.mit.edu/cummeRbund/>`_ does and makes it available through the Web interface. Unlike cummeRbund, multiple pipeline runs can be stored in the same database.

The primary goal of CuffBase is to make the results of cuffdiff pipeline accessible to a bench scientist.

Provides (so far) *very limited* plotting facilities via matplotlib.

Dependencies
=============
It's probably a good idea to manage these by setting up a virtual environment

* `django <http://www.djangoproject.com/>`_ version 1.6.
* `django-pagination <https://pypi.python.org/pypi/django-pagination>`_
* `matplotlib <http://matplotlib.org/>`_
* `brewer2mpl <https://github.com/jiffyclub/brewer2mpl.git>`_
* `pandas <http://pandas.pydata.org/pandas-docs/stable/>`_ (used in plot generation)
* `gunicorn <http://gunicorn.org>`_ -- for easy deployment
* data from the tophat/cufflinks pipeline (bunch of tab-delimited text files)

Deployment
===========

The recommended way to deploy CuffBase is to setup mod_wsgi in Apache2 or Gunicorn behind Nginx server. See ``ngs/settings.py`` file for the settings that need to be configured.

Quick start
============
You need to set up your database and specify relevant information (backend,
username, and password) in the ``ngs/settings.py`` file before trying to
import cuffdiff output results. For example, if using MySQL:

    ::
    
        mysql> create database <database-name> default charset utf8 collate utf8_general_ci;
        mysql> grant all on <database-name>.* to <user>@localhost identified by <password>;
    
and then the databases section of your ``ngs/settings.py`` file should read:
    
    ::
    
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

The live demo is up at `http://ngs.nudlerlab.info/demo/ <http://ngs.nudlerlab.info/demo/>`_. The site has a link to the mysql dump of the example data if you want to download and play with it locally.

to load the example database from the provided sql dump:

    ::
    
        $ gunzip -c ngs-dump-1.gz | mysql -u<user> -p<password> <database-name>

to import the cuffdiff output run this from the cuffbase directory:

    ::
    
        $ ./manage.py import_exp <path-to-cuffdiff-output>

to see available options for the ``import_exp`` command:

    ::
    
        $ ./manage.py import_exp --help

to start development server locally run this from the cuffbase directory:

    ::
    
        $ ./manage.py runserver --insecure

and cuffbase should be accessible in your browser at ``http://localhost:8080/cuff``

Caveats and limitations
=======================
I did my best trying to stick as close to the original cummeRbund
database schema as possible. I had, however, to use integer pks instead
of string pks in cummeRbund to make it play nicely with Django ORM. In 
addition, PhenoData, Feature, and Attribute tables are basically
placeholders. Not sure what to make of them.

* no tests -- the project was concieved as an ad-hoc solution with little consideration for future maintenance (I wasn't sure it'd work at all!)
* tests are sorely needed -- will be the first priority in moving forward
* no docs -- same as the tests
* not tested with anything but MySQL 5.5
* it was only tested on full cuffdiff output
* you will probably need a machine (or VPS) instance with at least 2 GB RAM. On a 4 GB, 4-core AMD desktop, importing the example dataset takes close to 5 min. This is slower than cummeRbund, but not by a large margin.
* because objects are created in bulk during the initial import, foreign key check fails when using InnoDB storage engine with MySQL database. The workaround is to either use MyISAM storage engine (include ``default-storage-engine = MyISAM`` in your ``/etc/mysql/my.cnf`` file prior to creating the databse) or turn off foreign key check for InnoDB engine on per-session basis.
* make sure to increase the ``maximum_packet_size`` parameter in ``/etc/mysql/my.cnf`` to somewhere around 64M, otherwise mysql will choke on importing big(ish) datasets.

Future plans
============

* refactor ``import_exp`` management command to use ``pandas``.
* interactive plotting with Bokeh
* tests
* docs (mostly on deployment)
* port to Python 3 (should be easy for anything but MySQL?)
* IPython notebook integration?

