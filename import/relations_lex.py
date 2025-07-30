from lxml import etree
from neo4j import GraphDatabase
import os
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

def import_con_rel_file(xml_path):
    logging.info(f"Processing: {xml_path}")
    tree = etree.parse(xml_path)
    root = tree.getroot()

    logging.info(f"Opening session on {NEO4J_URI} to database {NEO4J_DB} as user {NEO4J_USER}")
    with driver.session(database=NEO4J_DB) as session:
        logging.info(f"Processing Relations //lex_rel")
        for rel in root.xpath("//con_rel"):

            source = rel.get("from")
            target = rel.get("to")
            name = rel.get("name")
            direction = rel.get("dir")
            inverse = rel.get("inv")

            if not source or not target or not name or not direction:
                logging.info(f"Skipping malformed <con_rel>: {etree.tostring(rel)}")
                continue

            with driver.session(database=NEO4J_DB) as session:
                    
                # Forward direction
                if direction in ("one", "revert", "both"):
                    rel_type = name.upper()
                    
                    session.run(f"""
                        MATCH (s:Synset {{id: $source}}), (t:Synset {{id: $target}})
                        MERGE (s)-[:{rel_type}]->(t)
                    """, {"source": source, "target": target})

                # Reverse direction
                if direction in ("revert", "both") and inverse:
                    rel_type = inverse.upper()
                    session.run(f"""
                        MATCH (s:Synset {{id: $source}}), (t:Synset {{id: $target}})
                        MERGE (s)-[:{rel_type}]->(t)
                    """, {"source": target, "target": source})

def process_all_con_rel(xml_dir):
    for file in os.listdir(xml_dir):
        if file.endswith("_relations.xml"):
            path = os.path.join(xml_dir, file)
            import_con_rel_file(path)

process_all_con_rel(GERMANET_FOLDER)
