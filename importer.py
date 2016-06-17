# -*- coding: utf-8 -*-
import json
from collections import namedtuple

from botapi import Botagraph, BotApiError
from reliure.types import Text

NodeType = namedtuple("NodeType", "name description properties")
EdgeType = namedtuple("EdgeType", "name description properties")


# data source
data = json.load(open("./data/dict-amis.json"))

# Graph Definition

PDG_HOST = "http://g0v-tw.padagraph.io"
PDG_KEY = ""
GRAPHNAME = "Amis Dict"
DESCRIPTION = "lexical graph built from Amis Dictionnaries"
TAGS = ["Amis", "lexicon"]


# Node Types definitions

NodeWordForm = NodeType("Form", "", {"id": Text(),
                                     "label": Text()})
NodeStem = NodeType("Stem", "", {"id": Text(),"label": Text()})
NodeLexem = NodeType("Lexeme", "", {"id": Text(),
                                    "label": Text(),
                                    "form": Text(),
                                    "stem": Text(),
                                      "definition": Text(),
                                      "examples": Text()})

# Edge Types definitions

EdgeSynonyms = EdgeType("synonym", "", {})
EdgeStem = EdgeType("stem","",{})
EdgeHeteronymy  = EdgeType("heteronym", "", {})


# Graph creation

bot = Botagraph(PDG_HOST, PDG_KEY)
bot.create_graph(GRAPHNAME, {'description': DESCRIPTION, "tags": TAGS})


# Posting Nodes and Edges Types

nodetypes_uuids = {}
edgetypes_uuids = {}
for nt in [NodeStem, NodeLexem, NodeWordForm]: 
    nodetypes_uuids[nt.name] = bot.post_nodetype(GRAPHNAME, nt.name, nt.description, nt.properties)

for et in [EdgeStem, EdgeSynonyms, EdgeHeteronymy]:
    edgetypes_uuids[et.name] = bot.post_edgetype(GRAPHNAME, et.name, et.description, et.properties)


# Posting Nodes

def getNodesIterator():
    for entry in data:
        form = entry['title']
        yield { 'nodetype': nodetypes_uuids[NodeWordForm.name],
                'properties': {'id': (NodeWordForm.name, form),
                    'label': form}}
        stem = ""
        if 'stem' in entry:
            stem = entry['stem']
            yield { 'nodetype': nodetypes_uuids[NodeStem.name],
                'properties': {'id': (NodeStem.name, stem),
                    'label': stem}}
        i = 0
        for het in entry['heteronyms']:
            for lex in het['definitions']:
                i += 1 
                lexid = "%s-%d" % (form,i)
                examples = ""
                if "example" in lex:
                    examples = "\n".join([x.replace(u"\ufff9","- ")
                            .replace(u"\ufffa","").replace(u"\ufffb"," ") for x in lex['example']])
                props = {'form': form,
                        'id': (NodeLexem.name, lexid),
                        'label': lexid,
                        'stem': stem,
                        'definition': lex['def'],
                        'examples': examples}
                yield { 'nodetype': nodetypes_uuids[NodeLexem.name],
                        'properties': props}




nodes_uuids = {}
for node, uuid in bot.post_nodes(GRAPHNAME, getNodesIterator()):
    nid = node['properties']['id']
    nodes_uuids[nid] = uuid

# Posting Edges

def getEdgesIterator():
    for entry in data:
        form = entry['form']
        form_id = nodes_uuids[(NodeWordForm.name, form)]
        if 'stem' in entry:
            stem = entry['stem']
            stem_id = nodes_uuids[(NodeStem.name, stem)]
            yield {'edgetype': edgetypes_uuids[EdgeStem.name],
                    'source': form_id,
                    'target': stem_id,
                    'properties': {}}
        i = 0
        for het in entry['heteronyms']:
            for lex in het['definitions']:
                i += 1 
                lexid = nodes_uuids[(NodeLexem.name,"%s-%d" % (form,i))]
                yield {'edgetype': edgetypes_uuids[EdgeHeteronymy.name],
                        'source': form_id,
                        'target': lexid,
                        'properties': {}}
                for syn in lex.get('synonyms',[]):
                    syn_id = uuid.get((NodeWordForm.name, syn), None)
                    if syn_id is not None:
                        yield {'edgetype': edgetypes_uuids[EdgeSynonyms.name],
                                'source': form_id,
                                'target': syn_id,
                                'properties': {}}


list(bot.post_edges(GRAPHNAME, getEdgesIterator()))
