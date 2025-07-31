import requests
import mwparserfromhell
import json
import re
from collections import defaultdict

TEMPLATES = {
    "Bedeutungen": "definition",
    "Synonyme": "synonyms",
    "Gegenwörter": "antonyms",
    "Unterbegriffe": "hyponyms",
    "Beispiele": "examples"
}

def get_wikitext(term):
    url = f"https://de.wiktionary.org/w/rest.php/v1/page/{term}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Page not found: {term}")
    print(resp.json())
    return resp.json()["source"]

def extract_sections(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    sections = wikicode.get_sections(include_headings=True, levels=[3])
    entries = []

    for section in sections:
        heading = section.filter_headings()[0].title.strip() if section.filter_headings() else ""
        pos_match = re.search(r"\{\{Wortart\|([^\|]+)\|Deutsch\}\}", heading)
        part_of_speech = pos_match.group(1) if pos_match else "Unbekannt"

        # Collect lines
        lines = str(section).splitlines()
        current_template = None
        senses = defaultdict(lambda: defaultdict(list))

        for line in lines:
            line = line.strip()

            # Detect new section start: {{Bedeutungen}}, {{Synonyme}}, etc.
            match_template = re.match(r"\{\{(\w+)", line)
            if match_template:
                template_name = match_template.group(1)
                current_template = template_name if template_name in TEMPLATES else None
                continue

            if not current_template or not line.startswith(":"):
                continue

            # Match line starting with a sense marker, like :[1], :[2], :[?], etc.
            sense_match = re.match(r"^:\[([\d\?, ]+)\]\s*(.*)", line)
            if sense_match:
                sense_ids = [s.strip() for s in sense_match.group(1).split(",")]
                content = sense_match.group(2).strip()
                for sid in sense_ids:
                    senses[sid][TEMPLATES[current_template]].append(content)

        # Add definitions inline if only one sense and no [1], [2] markers
        if not senses and current_template == "Bedeutungen":
            # fallback to raw bullets
            for line in lines:
                if line.startswith("#"):
                    senses["1"]["definition"].append(line[1:].strip())

        entries.append({
            "part_of_speech": part_of_speech,
            "senses": senses
        })

    return entries

# --- Run and Print ---

term = "betont"
wikitext = get_wikitext(term)
parsed = extract_sections(wikitext)

# Convert defaultdict to normal dict for JSON
def normalize(obj):
    if isinstance(obj, defaultdict):
        return {k: normalize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize(x) for x in obj]
    else:
        return obj

result = {
    "title": term,
    "url": f"https://de.wiktionary.org/wiki/{term}",
    "entries": normalize(parsed)  # parsed is your existing output from extract_sections()
}

print(json.dumps(result, ensure_ascii=False, indent=2))

