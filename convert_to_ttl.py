# Python 3

# Command line parameters:
#    path to the .zip file containins .csv files
#    path of directory in which to put the .ttl files

# In terms.ttl, e:name should be rdfs:label
# In terms.ttl, maybe we should flush 'a e:Term' since these things are 
#  of all different types.
# Maybe Pages should instead be Taxons... or related to Taxons.
# Maybe e:scientific_name should be some DwC term.
# Maybe strip <i>...</i> off of scientific_name.

# Open zip file
# Open each .csv file
# for each row
#  emit <subject>
#  for each cell after the first
#   if cell is nonempty, increment counter
#   emit semicolon between cells, dot at end

import sys, os, csv, codecs, zipfile, argparse

def class_for_filename(filename):
    if filename == 'metadata':
        return 'Metadatum'
    elif filename.endswith('s'):
        # pages terms traits
        return filename[0:-1].capitalize()
    return filename.capitalize()

def is_iri_like(value):
    return ((value.startswith('http://') or
             value.startswith('https://')) and
            not ' Accessed at ' in value)

# This is just a mistake
# http://eol.org/schema/terms/average\n,average n,,

def clean_iri(value):
    return value.strip() \
                .replace(' ', '%20') \
                .replace('\\n', '%10')

def id_to_turtle(id, clas):
    if is_iri_like(id):
        return "<%s>" % clean_iri(id)
    elif ' ' in id or '(' in id or '/' in id or '?' in id or ':' in id or len(id) == 0:
        return None
    elif clas == 'Page':
        return '<https://eol.org/pages/%s>' % id
    else:
        return '<https://ld.eol.org/%s/%s>' % (clas, id)

def convert_to_ttl(path, outdir):
    archive = zipfile.ZipFile(path, 'r')
    zip_triples = 0
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    for filename in ['traits', 'metadata', 'pages', 'terms']:
        csv_path = 'trait_bank/%s.csv' % (filename,)
        ttl_path = os.path.join(outdir, '%s.ttl' % (filename,))
        clas = class_for_filename(filename)
        class_uri = "e:%s" % (clas,)
        with archive.open(csv_path, 'r') as raw_infile:
            with open(ttl_path, 'w', encoding='utf8') as outfile:
                # To do: define prefix
                infile = codecs.iterdecode(raw_infile, 'utf-8')
                rows = 0
                triples = 0
                nulls = 0
                r = csv.reader(infile)
                header = r.__next__()
                print("%s: %s" % (clas, header[1:]))
                outfile.write('@prefix e: <http://eol.org/schema/>\n')
                column_names = header
                for row in r:
                    rows += 1
                    turtle = id_to_turtle(row[0], clas)
                    if turtle == None: continue
                    if column_names[0] == 'uri' and not is_iri_like(row[0]):
                        # Punt, row is ill-formed
                        continue
                    outfile.write('%s a e:%s' % (turtle, clas))
                    for (column_name, value) in zip(column_names, row):
                        if len(value) == 0:
                            nulls += 1
                        elif column_name == 'uri':
                            pass
                        else:
                            outfile.write(';\n ')
                            # Write property + value
                            if is_iri_like(value):
                                if column_name.endswith('_uri'):
                                    column_name = column_name[0:-4]
                                value = clean_iri(value)
                                outfile.write('e:%s <%s>' % (column_name, value))
                            elif column_name == 'parent_id':
                                outfile.write('e:parent_page %s' % id_to_turtle(value, 'Page'))
                            elif column_name == 'page_id':
                                # in traits table
                                outfile.write('e:page %s' % id_to_turtle(value, 'Page'))
                            elif column_name == 'trait_eol_pk':
                                outfile.write('e:trait %s' % id_to_turtle(value, 'Trait'))
                            elif value.isdigit():
                                # should pick up floats as well
                                outfile.write('e:%s %s' % (column_name, value))
                            else:
                                r = value.replace('\\', '\\\\')
                                r = r.replace('\t', '\\t')
                                r = r.replace('\r', '\\r')    # return
                                r = r.replace('\n', '\\n')
                                r = r.replace('"', '\\"')
                                outfile.write('e:%s "%s"' % (column_name, r))
                            triples += 1
                    outfile.write('.\n')
                print('%25s: %7s rows, %8s triples, %8s empty' % (csv_path, rows, triples, nulls))
                zip_triples += triples
    print('%s triples' % (zip_triples,))

convert_to_ttl(sys.argv[1], sys.argv[2])
