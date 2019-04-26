# Quick and dirty linked data prototype for traitbank

## Idea

  * Pick a well supported free-software triple store, one with good
    SPARQL support, and capable of hosting traitbank (which would be 100
    million triples or so)
  * Convert the traitbank .csv dump to turtle
  * Load the .ttl files into the triple store
  * Provide access to the sparql endpoint (read-only)
  * Use timeouts and/or logins to forestall DoS 'attacks' (or mistakes)

## Realization

I picked Jena Fuseki for this experiment.  It's pretty
easy to install.  The primary documentation is awful, but there are some
third-party 'howto' posts that are very helpful.

I wrote a kind of stupid python3 program to convert the traitbank .zip
file to turtle.  Actually I only worked with a small subset (family
Felidae, EOL page id 7674), which as of November 2018 was 144 taxa,
8769 trait records, 28628 metadata records, and 8017 terms.

This code is just a proof of concept; it is not meant for production
use.  It represents only about two days of work.

## HOWTO

  - make sure Java is installed (I used Java 8)
  - clone this repository and enter its top level directory
  - download Jena (I used version 3.10) and Fuseki
      (see https://jena.apache.org/download/ )

Shell setup: (the .gz files might be in `~/Downloads/` or somewhere
else depending on how you did the downloads)

    tar xzf apache-jena-3.10.0.tar.gz
    tar xzf apache-jena-fuseki-3.10.0.tar.gz
    export JENA_HOME=apache-jena-3.10.0
    export FUSEKI_HOME=apache-jena-fuseki-3.10.0

Scripts are in `$JENA_HOME/bin/`.  Smoke test: `$JENA_HOME/bin/sparql --version`

The repository contains a small sample .zip file.  If you want to make
others, you'll need to fetch trait records from EOL using the
`traits_dumper.rb` script from the `eol_website` repository; you'll
also need a "power user" API token (see 
[the API documentation](https://github.com/EOL/eol_website/blob/master/doc/api.md)).
There is a suitable rule in the Makefile for obtaining a .zip , but it
requires that the exported shell variable point to a directory
containing (a) the API token in `api.token` and (b) a clone of the
eol_website repository.

Convert traitbank csv to turtle: (this just picks up the Felidae zip file from the repository, but it is easy to drive it from a more significant traitbank zip file, perhaps even the whole thing)

    make convert

Load turtle into the Fuseki TDB persistent triple store:

    make load

(There are a number of errors as the Turtle loads.  These are not
fatal but eventually they ought to be fixed.)

Start the server:

    make serve

or

    make serve &

or use `nohup` or `/etc/init.d`, etc.

Now visit Fuseki in a browser.  For example, if the browser is on the
same computer as the Fuseki server, visit:

    http://localhost:3030/

Fuseki generates JSON sparql query result format by default.  The
format choice is selectable via the UI, or in a way prescribed by the
[SPARQL protocol](https://www.w3.org/TR/sparql11-overview/)).

Fuseki can generate JSON-LD for SPARQL `CONSTRUCT` commands although
turtle is the default.  This would be useful for providing specialized
linked data services (e.g. for reviving the v2 API, should we so
choose).

A proper SPARQL endpoint is available (instructions TBD).

## Security

Fuseki has no security infrastructure (other than what one finds in
`shiro.ini` which I don't understand).  Visitors to the Fuseki port
can perform updates, deletions, and so on.  To make an open endpoint,
one might use apache ProxyPass or some similar feature that allows
fine-grained access control.  Nginx certainly has something
equivalent.  Alternatively, one could deploy the .war file in tomcat,
and I'm sure other arrangements are possible as well.

## Resource use

  * The Felidae .zip file is about .6M
  * The Turtle files for that .zip file come to about 11M
  * Space on disk used by the persistent store is 18M

The .zip file for _all_ of traitbank is 461M, which by linear
extrapolation would turn into 14G on disk for persistent triple
storage (not that much I guess).  I don't know what this means in
terms of RAM.  I have no idea what query performance would be at
scale, but it is claimed that Jena does pretty well.

## What the turtle looks like

Below is a small sample of what the triple store contents look like
when rendered as Turtle.  The domain `ld.eol.org` doesn't exist, it is
just a placeholder.  We'd have to define and document a proper RDFS
schema to use with this RDF.

    @prefix e:     <http://ld.eol.org/schema/> .

    <https://ld.eol.org/Metadatum/MetaTrait-116639925>
            a            e:Metadatum ;
            e:eol_pk     "MetaTrait-116639925" ;
            e:predicate  <http://rs.tdwg.org/dwc/terms/measurementUnit> ;
            e:trait      <https://ld.eol.org/Trait/R788-PK72639112> ;
            e:value      <http://purl.obolibrary.org/obo/UO_0000021> .

    <https://ld.eol.org/Trait/R788-PK72639112>
            a                     e:Trait ;
            e:eol_pk              "R788-PK72639112" ;
            e:measurement         7257 ;
            e:normal_measurement  7257 ;
            e:normal_units        <http://purl.obolibrary.org/obo/UO_0000021> ;
            e:page                <https://eol.org/pages/328671> ;
            e:predicate           <http://purl.obolibrary.org/obo/VT_0001259> ;
            e:resource_id         694 ;
            e:scientific_name     "<i>Felis chaus</i>" ;
            e:units               <http://purl.obolibrary.org/obo/UO_0000021> .

    <http://rs.tdwg.org/dwc/terms/measurementUnit>
            a       e:Term ;
            e:name  "measurement unit" ;
            e:type  "metadata" .

    <http://purl.obolibrary.org/obo/UO_0000021>
            a       e:Term ;
            e:name  "g" ;
            e:type  "value" .

    <https://ld.eol.org/Metadatum/MetaTrait-116639926>
            a            e:Metadatum ;
            e:eol_pk     "MetaTrait-116639926" ;
            e:predicate  <http://eol.org/schema/terms/statisticalMethod> ;
            e:trait      <https://ld.eol.org/Trait/R788-PK72639112> ;
            e:value      <http://eol.org/schema/terms/average> .
