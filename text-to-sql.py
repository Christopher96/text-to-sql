import nltk
from nltk.parse.recursivedescent import RecursiveDescentParser
from nltk import CFG

cfgstring = """
QUERY -> QUERY_MANY | QUERY_SINGLE
QUERY_SINGLE -> SINGLE AGGR COL
QUERY_MANY -> AGGR WHERE
AGGR -> MIN | MAX | COUNT | ALL
WHERE -> OP COL
MIN -> 'the' 'least'
MAX -> 'the' 'most'
ALL -> 'show' 'me' | 'find' | 'list'
COUNT -> 'how' 'many'
SINGLE -> 'who' 'has'
OP -> 'are'
COL -> 'people' | 'male' | 'salary'
"""

grammar = CFG.fromstring(cfgstring)

rd = RecursiveDescentParser(grammar)

def buildQuery(parsed):
    query = "SELECT "
    query_type = parsed[0]
    if(query_type.label() == "QUERY_MANY"):
        aggr_type = query_type[0]
        if(aggr_type.label() == "ALL"):
            query += "* FROM"
        else:
            query += "COUNT"
    elif(query_type.label() == "QUERY_SINGLE"):
        aggr_type = query_type[1][0]
        aggr_col = query_type[2]
        print(aggr_col)
    # for subtree in parsed.subtrees():
    #     print(subtree)
    print('\n')
    return

sentences = []

with open('sample.txt', 'r') as f:
    for line in f:
        line = line.replace('\n', '')
        sentences.append(line)

for sent in sentences:
    sent = sent.split()
    print(sent)
    for parsed in rd.parse(sent):
        buildQuery(parsed)

