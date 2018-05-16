# -*- coding: utf-8 -*-
import json
from collections import namedtuple

#from botapi import Botagraph, BotApiError
#from reliure.types import Text

NodeType = namedtuple("NodeType", "name description properties")
EdgeType = namedtuple("EdgeType", "name description properties")


# data source
data = json.load(open("/tmp/dict-amis-safolu.json"))

# Graph Definition

PDG_HOST = "http://foldr.padagraph.io/dict-amis"
PDG_KEY = ""
GRAPHNAME = "Amis Dict"
DESCRIPTION = "lexical graph built from Amis Dictionnaries"
TAGS = ["Amis", "lexicon"]


# Node Types definitions

NodeWordForm = NodeType("Form", "", ["id", "label"])
NodeStem = NodeType("Stem", "", ["id", "label"])
NodeLexem = NodeType("Lexeme", "", ["id",
                                    "label",
                                    "form",
                                    "stem",
                                    "definition",
                                    "examples"])

# Edge Types definitions

EdgeSynonyms = EdgeType("synonym", "", {})
EdgeStem = EdgeType("stem","",{})
EdgeHeteronymy  = EdgeType("heteronym", "", {})


# Graph creation


#for nt in [NodeStem, NodeLexem, NodeWordForm]: 
#for et in [EdgeStem, EdgeSynonyms, EdgeHeteronymy]:


# Posting Nodes

def getNodesIterator():
    for entry in data:
        form = entry['title']
        #yield { 'nodetype': NodeWordForm.name,
        #        'properties': {'id': (NodeWordForm.name, form),
        #            'label': form}}
        stem = ""
        if 'stem' in entry:
            stem = entry['stem']
            #yield { 'nodetype': NodeStem.name,
            #    'properties': {'id': (NodeStem.name, stem),
            #        'label': stem}}
        i = 0
        for het in entry['heteronyms']:
            for lex in het['definitions']:
                i += 1 
                lexid = "%s-%d" % (form,i)
                examples = ""
                if "example" in lex:
                    examples = "\n".join([x.replace(u"\ufff9","- ")
                            .replace(u"\ufffa","").replace(u"\ufffb"," ") for x in lex['example']])
                props = [form,
                        lexid,
                        stem,
                        lex['def'].replace(",","，"),
                        examples.replace("\n"," / ").replace(",","，")]
                yield { 'nodetype': NodeLexem.name,
                        'properties': props}


print("@Lexeme: %form, #label, %stem, def, ex")
for n in getNodesIterator():
    print(", ".join(n['properties']))
