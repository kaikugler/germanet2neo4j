# germanet2neo4j
scripts to import germanet xml into a neo4j database 

## How to import germanet into your Neo4j- or ONg-Database

1. set your Database-URI, user, database, password and path to the germanet-XML-files in the config-file
2. run `nodes_synset_lexunits.py` to create all Synset- and LexUnit-nodes
3. run `relations_con.py` to create the relations between Synsets
4. run `relations_lex.py` to create the relations between LexUnits
5. run `paraphrases.py` to add the paraphrases to the Synset-nodes as a property
 
