To create a Whoosh Index from the sample of TREC Aquaint documents you will need to perform the following steps.

Note: that to the pre-preprocessing steps (1-2) have already been performed (and the resulting data is already in the GitHub repo).
The scripts to perform the pre-processing are included so that if you have access to the TREC Aquaint collection you can quickly prepare it.


Make the scripts in sample_data executable.

chmod u+x *.sh

1. For each TREC data file, special characters need to be removed, otherwise the parser will bunk out.

./fix_special_chars.sh trec_aquaint/


2. For each TREC data file, it needs to be converted to be in <XML> format, so that the XML reader can read in the entire file.
(to do this, we need to add in <DOCS> at the begginning of each file, and </DOCS> at the end.


./convert_to_xml.sh trec_aquaint/

This will convert each TREC data file and put it into /xml/trec_aquaint/

3. Make a list of files to feed to the indexer script.

./make_file_list.sh

4. Run the indexing script.

python create_trec_whoosh_index.py


These scripts show you how to index the TREC Aquaint collection, but could be used to process other TREC Collections.