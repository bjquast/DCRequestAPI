# DCRequestAPI

The DCRequestAPI should provide access to data stored in one or more [DiversityCollection](https://www.diversityworkbench.net/dwb_main.html) database instances. 
It uses ElasticSearch to provide fast search options. The DCRequestAPI handles access rights as set in Withholding fields in DiversityCollection database.
Logged on users have access to all data in their projects, unauthrorized users can only access public data.


## Setup

### On bare metal

#### System requirements

 - Python 3
 - an ODBC Driver and TDS
 - MySQL
 - git

E. g. install system requirements in Ubuntu:

    sudo apt-get install software-properties-common python3-dev python3-setuptools python3-pip unixodbc unixodbc-dev tdsodbc mysql-server mysql-client git


 - A running ElasticSearch instance (see [Installing ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)


#### Set up and activate a virtual python environment

    python3 -m venv ./dcrequestapi
    cd ./dcrequestapi
    source bin/activate

#### Download sources

    git clone https://github.com/bjquast/DCRequestAPI.git


#### Set up DCRequestAPI in virtual environment

    cd DCRequestAPI
    python3 setup.py develop


#### Configuration

Copy the file ./config.ini.template to ./config.ini:

    cp ./config.ini.template ./config.ini

Add at least one connection to a DiversityCollection database in a section with the prefix **data_source_**. 
Multiple databases can be used when more than one of these sections are in the config.ini file. These sections must have a unique 
name after the **data_source_**-prefix and a unique **accronym** entry. 

A MySQL database must be available for the **dwb_authentication**. This database can be empty, but must be available for a MySQL root user with 
the password given in the entry **root_password**.    

The **taxamergerdb** entry is used to provide a MySQL database with a curated taxonomy that is used to match the identifications 
in DiversityCollection with. This **taxamergerdb** can be a database that is generated by merging several DiversityTaxonNames databases so that the
relations between Identifications in DiversityCollection and DiversityTaxonNames can be preserved. 
The code for generating such a merged database is available under: [tnt_taxa_merger](https://github.com/ZFMK/tnt_taxa_merger). 
When no taxamergerdb is available the entry **skip_taxa_db** must be set to a true value (True, true, or 1).


 










### docker
