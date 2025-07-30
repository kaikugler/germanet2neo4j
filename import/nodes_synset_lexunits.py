import os
from lxml import etree
from neo4j import GraphDatabase
import configparser
import logging

conf = configparser.ConfigParser()
conf.read("config.ini")
NEO4J_URI = conf.get('Connection', 'Uri')
NEO4J_USER = conf.get('Connection', 'User')
NEO4J_PASSWORD = conf.get('Connection', 'Password')
NEO4J_DB = conf.get('Connection', 'Database')

GERMANET_FOLDER = conf.get('Data', 'Path')

logging.basicConfig(level=logging.INFO)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ---------------------
# Neo4j Helper Functions
# ---------------------

def create_synset(tx, synset_id, s_class, category):
    tx.run("""
        MERGE (s:Synset {id: $synset_id})
        SET s.class = $s_class, s.category = $category
    """, synset_id=synset_id, s_class=s_class, category=category)

def create_lexunit(tx, lexunit_id, orth_form, orth_vars, sense, ne, art, sty, source, synset_id):
    tx.run("""
        MERGE (l:LexUnit {id: $lexunit_id})
        SET l.orthForm = $orth_form, l.orthVar = $orth_vars, l.sense = $sense, l.namedEntity = $ne, l.artificial = $art, l.styleMarking = $sty, l.source = $source
        WITH l
        MATCH (s:Synset {id: $synset_id})
        MERGE (l)-[:BELONGS_TO]->(s)
    """, lexunit_id=lexunit_id, orth_form=orth_form, orth_vars=orth_vars, sense=sense, ne=ne, art=art, sty=sty, source=source, synset_id=synset_id)

# ---------------------
# XML Import Logic
# ---------------------
def import_germanet_file(xml_file):
    print(f"📄 Processing: {xml_file}")
    tree = etree.parse(xml_file)
    root = tree.getroot()

    with driver.session(database=NEO4J_DB) as session:
        # First pass: Create Synsets and LexUnits
        for synset in root.findall(".//synset"):
            synset_id = synset.get("id")
            category = synset.get("category")
            s_class = synset.get("class")

            session.write_transaction(create_synset, synset_id, s_class, category)
            logging.info(f"💾 Synset:{synset_id}")

            for lex_unit in synset.findall("lexUnit"):
                lexunit_id = lex_unit.get("id")
                sense = lex_unit.get("sense")
                ne = lex_unit.get("namedEntity")
                art = lex_unit.get("artificial")
                sty = lex_unit.get("styleMarking")
                source = lex_unit.get("source")
                orth_form = [o.text for o in lex_unit.findall("orthForm")]
                orth_vars = [o.text for o in lex_unit.findall("orthVar")]
                # orth_form = lex_unit.get("orthForm")
                session.write_transaction(create_lexunit, lexunit_id, orth_form, orth_vars, sense, ne, art, sty, source, synset_id)
                logging.info(f"💾 LexUnit:{synset_id}")

# ---------------------
# Process All XML Files
# ---------------------
def import_all_germanet_files(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".xml"):
            xml_path = os.path.join(folder, filename)
            import_germanet_file(xml_path)
    logging.info("✅ All files imported into Neo4j database:", NEO4J_DB)

# ---------------------
# Main
# ---------------------
if __name__ == "__main__":
    import_all_germanet_files(GERMANET_FOLDER)
