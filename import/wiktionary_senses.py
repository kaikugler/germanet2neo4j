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

def insert_data(tx, item):
    cypher = """
    MATCH (lu:LexUnit {id: $lexUnitId})
    MERGE (wa:WiktionaryLemma {id:$wiktionaryId})
    CREATE (ws:WiktionarySense {id:$wiktionaryId+'_'+$wiktionarySenseId})
      SET ws.wiktionarySenseId = $wiktionarySenseId, ws.paraphrase = $wiktionarySense, ws.wiktionaryId = $wiktionaryId, ws.edited = $edited
    MERGE (lu)-[:HAS_SENSE]->(ws)
    MERGE (wa)-[:HAS_SENSE]->(ws)
    """
    tx.run(
        cypher,
        lexUnitId=item["lexUnitId"],
        wiktionarySense=item["wiktionarySense"],
        wiktionarySenseId=item["wiktionarySenseId"],
        wiktionaryId=item["wiktionaryId"],
        edited=item["edited"]
    )

# ---------------------
# XML Import Logic
# ---------------------
def import_germanet_file(xml_file):
    print(f"📄 Processing: {xml_file}")
    tree = etree.parse(xml_file)
    root = tree.getroot()

    with driver.session(database=NEO4J_DB) as session:
        
        item = {}
        for para in root.findall(".//wiktionaryParaphrase"):
            item["lexUnitId"] = para.get("lexUnitId")
            item["wiktionarySense"] = para.get("wiktionarySense")
            item["wiktionarySenseId"] = para.get("wiktionarySenseId")
            item["wiktionaryId"] = para.get("wiktionaryId")
            item["edited"] = para.get("edited")

            session.write_transaction(insert_data, item)
            logging.info(f"💾 WiktionarySense:{item['wiktionaryId']}")

# ---------------------
# Process All XML Files
# ---------------------
def import_all_germanet_files(folder):
    for filename in os.listdir(folder):
        if filename.startswith("wiktionaryParaphrases"):
            xml_path = os.path.join(folder, filename)
            import_germanet_file(xml_path)
    logging.info("✅ All files imported into Neo4j database")

# ---------------------
# Main
# ---------------------
if __name__ == "__main__":
    import_all_germanet_files(GERMANET_FOLDER)
