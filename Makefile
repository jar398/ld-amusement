
# Need to define APACHE_JENA_BIN etc
#
# export JENA_HOME=~/Downloads/apache-jena-3.10.0
# export FUSEKI_HOME=~/Downloads/apache-jena-fuseki-3.10.0
# APACHE_JENA_BIN=$JENA_HOME/bin
# JENA_FUSEKI_JAR=$FUSEKI_HOME/fuseki-server.jar


all: load

serve: data/dataForTDB/nodes.dat
	$$FUSEKI_HOME/fuseki-server --loc=data/dataForTDB /traitbank
	echo http://localhost:3030/traitbank

load: data/dataForTDB/nodes.dat

data/dataForTDB/nodes.dat: felidae-ttl/terms.ttl
	time $$APACHE_JENA_BIN/tdbloader2 --loc=data/dataForTDB felidae-ttl/*.ttl

convert: felidae-ttl/terms.ttl

felidae-ttl/terms.ttl: felidae.zip convert_to_ttl.py
	python3 convert_to_ttl.py felidae.zip felidae-ttl

