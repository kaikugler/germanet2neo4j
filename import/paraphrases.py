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

def add_paraphrase(tx, synset_id, para):
    result = tx.run("""
        MATCH (n:Synset {id: $synset_id})
        SET n.paraphrase = $para
        RETURN n
    """, synset_id=synset_id, para=para)
    
    logging.info(f"💾 Updating synset-id:{synset_id}\t SET paraphrase:{para}")

# ---------------------
# XML parsing
# ---------------------

def process_germanet_file(xml_file):
    logging.info(f"📄 Processing: {xml_file}")
    tree = etree.parse(xml_file)
    root = tree.getroot()

    with driver.session(database=NEO4J_DB) as session:
        # Find Synsets with paraphrases
        for synset in root.findall(".//synset"):
            synset_id = synset.get("id")
            para = [o.text for o in synset.findall("paraphrase")]
            if para:
                # no empty paraphrases
                if para[0]:
                    try:
                        session.execute_write(add_paraphrase, synset_id, para[0])
                    except CypherSyntaxError as e:
                        logging.error("⛔ Syntax error:", e)
                    except ClientError as e:
                        logging.error("⛔ Client error:", e)
                    except Neo4jError as e:
                        logging.error("⛔ Neo4j error:", e)
                    

# ---------------------
# Process All XML Files
# ---------------------
def process_all_germanet_files(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".xml"):
            xml_path = os.path.join(folder, filename)
            process_germanet_file(xml_path)
    logging.info("✅ All files processed")

# ---------------------
# Main
# ---------------------
if __name__ == "__main__":
    process_all_germanet_files(GERMANET_FOLDER)
