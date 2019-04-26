# Rules for various operations related to Fuseki SPARQL service for traitbank

# Need to define APACHE_JENA_BIN etc
#
# export JENA_HOME=~/Downloads/apache-jena-3.10.0
# export FUSEKI_HOME=~/Downloads/apache-jena-fuseki-3.10.0
# export EOL=/dsk/jar/a/eol

TAXON=felidae
TAXON_PAGE=7674

all: load

serve: data/dataForTDB/nodes.dat
	$$FUSEKI_HOME/fuseki-server --loc=data/dataForTDB /traitbank
	echo http://localhost:3030/traitbank

load: data/dataForTDB/nodes.dat

data/dataForTDB/nodes.dat: $(TAXON)-ttl/terms.ttl
	rm -rf data/dataForTDB/*
	mkdir -p data/dataForTDB
	time $$JENA_HOME/bin/tdbloader2 --loc=data/dataForTDB $(TAXON)-ttl/*.ttl

convert: $(TAXON)-ttl/terms.ttl

$(TAXON)-ttl/terms.ttl: $(TAXON).zip convert_to_ttl.py
	python3 convert_to_ttl.py $(TAXON).zip $(TAXON)-ttl

$(TAXON).zip:
	ID=$(TAXON_PAGE) CHUNK=10000 TOKEN=`cat $$EOL/api.token` ZIP=$(TAXON).zip \
          time ruby -r $$EOL/eol_website/lib/traits_dumper.rb -e TraitsDumper.main
