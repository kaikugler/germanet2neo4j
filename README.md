# germanet2neo4j
python-scripts to import GermaNet XML into a Neo4j database 

## How to import [GermaNet](https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/allg-sprachwissenschaft-computerlinguistik/ressourcen/lexica/germanet-1/) (see [^3] and [^4])
into your Neo4j- or ONg-Database

### prepare the database by importing the basic nodes

1. set your Database-URI, user, database, password and path to the germanet-XML-files in the config-file
2. run `nodes_synset_lexunits.py` to create all Synset- and LexUnit-nodes

In step 2, the nodes are created. The script looks for `<synset>` tags in the XML files, creates Synset-nodes 
and LexUnit-nodes for every `<lexUnit>` in the `<synset>`. It also creates `:BELONGS_TO` relations 
between the LexUnits and the Synsets.

### add the relations

3. run `relations_con.py` to create the relations between Synsets
4. run `relations_lex.py` to create the relations between LexUnits

The scripts parse the `*_relations.xml` file(s). If you just want the relations between 
Synset nodes (`<con_rel>`) in your database, only run the script in step 3. It creates 
relations in both directions (e.g. `:HAS_HYPERNYM` and `:HAS_HYPONYM`) if available.
The script in step 4 does the same for relations between LexUnits (`<lex_rel>`).

For further information about the lemmata and semantic relations in GermaNet please see [Beschreibung](https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/allg-sprachwissenschaft-computerlinguistik/ressourcen/lexica/germanet-1/beschreibung/) and [^3].


### optional: add paraphrases

5. run `paraphrases.py` to add the paraphrases to the Synset-nodes as a property
6. run `wiktionary_senses.py` to add WiktionaryLemma and WiktionarySenses nodes

Some Synsets have a `<paraphrase>`. The script in step 5 adds these paraphrases as
a property to the Synset-nodes.
If you want to add the [wiktionaryParaphrases](https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/allg-sprachwissenschaft-computerlinguistik/ressourcen/lexica/germanet-1/beschreibung/wiktionary-definitions/)
download the `wiktionaryParahrase-*.xml`-files to your germanet-folder and run the script in step 6:  For every `<wiktionaryParaphrase>` it will
add a WiktionarySense-node to the database, a relation to the LexUnit and will add an WiktionaryLemma-node (if it does not already exist). The lemma node 
corresponds to the wiktionary article from which the sense originates.
For the Wiktionary-Mapping see [^1] and [^2].

## Examples

### Wiktionary Paraphrases

If you imported the wiktionaryPhrases, you can get subgraphs like this:
![image](/images/graph_w11677.png)

There are two senses for the WiktionaryLemma `w11677` [Blues](https://de.wiktionary.org/wiki/Blues) (based on the mapped data in the original `wiktionaryParaphrases-nomen.xml`-file): "afroamerikanische Musikrichtung" and "ein Tanz" 
with the WiktionarySense nodes `w11677_0` and `w11677_2`. The are related to the LexUnits `l37183` and `l25067` (Blues). The first one has a synonym "Bluesmusik" (`l37184`).
"Blues" (`l37183`) and "Bluesmusik" (`l37184`) belong to the Synset `s27224`.

To get the Wikipedia paraphrase for the synset `s27224` you can run

```
MATCH (syn:Synset {id: "s27224"})<-[:BELONGS_TO]-(lu:LexUnit)-[:HAS_SENSE]->(ws:WiktionarySense)
RETURN ws.paraphrase AS paraphrase
```

resulting in "amerikanische Musikrichtung".

To map the Sysets to the senses from the Wiktionary articles, use a query like:

```
MATCH (syn:Synset)<-[:BELONGS_TO]-(lu:LexUnit)-[:HAS_SENSE]->(ws:WiktionarySense)
```

## References 

[^1]: Verena Henrich, Erhard Hinrichs und Tatiana Vodolazova (2014): Aligning GermaNet Senses with Wiktionary Sense Definitions. In Zygmunt Vetulani and Joseph Mariani (eds.): Human Language Technology: Challenges for Computer Science and Linguistics, Lecture Notes in Computer Science, Vol. 8387, pp. 329-342.
[^2]: Verena Henrich, Erhard Hinrichs und Tatiana Vodolazova (2011): Semi-Automatic Extension of GermaNet with Sense Definitions from Wiktionary. In Proceedings of 5th Language & Technology Conference (LTC 2011), Poznań, Poland, pp. 126-130. 
[^3]: Hamp, Birgit und Helmut Feldweg. "GermaNet - a Lexical-Semantic Net for German." Proceedings of the ACL workshop Automatic Information Extraction and Building of Lexical Semantic Resources for NLP Applications. Madrid, 1997.
[^4]: Henrich, Verena und Erhard Hinrichs. "GernEdiT - The GermaNet Editing Tool". Proceedings of the Seventh Conference on International Language Resources and Evaluation (LREC 2010). Valletta, Malta, May 2010, pp. 2228-2235. 

