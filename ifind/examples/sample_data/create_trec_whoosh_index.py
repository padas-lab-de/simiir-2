__author__ = 'leif'
from xml.dom import minidom
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
import os


def readDataFiles( datafile ):
    filelist = []
    f = open(datafile,"rb")
    for line in f.readlines():
        filelist.append(line.rstrip())
        #print line
    f.close()
    return filelist

def getText(nodelist):
    rc = [u'']
    for nl in nodelist:
        if nl.firstChild:
            rc.append(nl.firstChild.data)
    return u''.join(rc)



stemmer = StemmingAnalyzer()


#This is the schema that the whooshtrec search engine in ifind expects.
schema = Schema(docid=TEXT(stored=True), title=TEXT(analyzer=stemmer, stored=True), content=TEXT(analyzer=stemmer, stored=True),
                timedate=TEXT(stored=True), source=TEXT(stored=True), alltext=TEXT(stored=True) )


work_dir = os.getcwd()
my_whoosh_doc_index_dir = os.path.join(work_dir, 'index')
xml_files = os.path.join(work_dir,'aquaint_xml.list')

ix = create_in(my_whoosh_doc_index_dir, schema)


files_to_process = readDataFiles(xml_files)

writer = ix.writer(limitmb=1024, procs=1, multisegment=False)
for dfile in files_to_process:
    print("Processing File: " + str(dfile))
    xmldoc = minidom.parse(dfile.decode('utf-8'))
    for node in xmldoc.getElementsByTagName("DOC"):
        tmp = node.getElementsByTagName('DOCNO')
        ndocid = getText(tmp)
        ndocid = ndocid.strip()


        print("Processing: *"+str(ndocid)+"*")
        tmp = node.getElementsByTagName('HEADLINE')
        ntitle = getText(tmp)

        textnode = node.getElementsByTagName('TEXT')
        ncontent = getText(textnode)
        ptext = ""
        for pnode in textnode[0].getElementsByTagName('P'):
            ptext = ptext + "<p>" + pnode.firstChild.data + "</p>"


        ncontent = ncontent + " " +  ptext
        tmp = node.getElementsByTagName('DATE_TIME')
        ntimedate = getText(tmp)

        nsource = u""
        if ndocid.startswith('APW'):
            nsource = u"Associated Press Worldwide News Service"
        if ndocid.startswith('XIE'):
            nsource = u"Xinhua News Service"
        if ndocid.startswith('NYT'):
            nsource = u"New York Times News Service"


        nalltext = ntitle + " " + ncontent + " " + nsource

        writer.add_document(docid=ndocid, title=ntitle, content=ncontent, timedate=ntimedate, source=nsource, alltext=nalltext)

print("Committing documents to index (takes some time): " + str(dfile))
writer.commit()

