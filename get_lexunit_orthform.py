import xml.etree.ElementTree as ET
from neo4j import GraphDatabase
import json

# Neo4j credentials
NEO4J_URI = "bolt://136.199.93.37:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Aneo4!37DE"
XML = "/home/kai/GN_V190_XML/wiktionaryParaphrases-nomen.xml"

# 1. Parse XML and collect entries
def parse_wiktionary_paraphrases(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    entries = []
    for elem in root.iter("wiktionaryParaphrase"):
        lex_id = elem.attrib.get("lexUnitId")
        sense = elem.attrib.get("wiktionarySense")
        sense_id = elem.attrib.get("wiktionarySenseId")
        if lex_id:
            entries.append({
                "lexUnitId": lex_id,
                "wiktionarySense": sense,
                "wiktionarySenseId": sense_id
            })
    return entries

# 2. Query Neo4j for orthForm
def get_orth_forms(driver, lex_ids):
    query = """
    UNWIND $ids AS id
    MATCH (l:LexUnit {id: id})
    RETURN id, l.orthForms AS orthForm
    """
    with driver.session() as session:
        result = session.run(query, ids=list(lex_ids))
        return {record["id"]: record["orthForm"] for record in result}

# 3. Combine and enrich results
def enrich_with_orthform(entries, orth_map):
    for e in entries:
        e["orthForm"] = orth_map.get(e["lexUnitId"], None)
    return entries

# 4. Main
def main():
    xml_file = XML 
    entries = parse_wiktionary_paraphrases(xml_file)
    lex_ids = set(e["lexUnitId"] for e in entries)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    orth_forms = get_orth_forms(driver, lex_ids)
    driver.close()

    enriched = enrich_with_orthform(entries, orth_forms)

    # Print result as JSON
    print(json.dumps(enriched, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
