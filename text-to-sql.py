import nltk
from nltk.parse.recursivedescent import RecursiveDescentParser
from nltk import CFG

tags = ["NUM"]

def populateGrammar(sent):
    f = open("grammar.txt", "r")
    grammar = f.read()

    split = sent.split()
    tagged = nltk.pos_tag(split, tagset="universal")
    for i in range(len(split)):
        word, tag = tagged[i]
        if tag in tags:
            grammar += f"{tag} -> '{word}'\n"

    print(grammar)

    return CFG.fromstring(grammar)


def whereToQuery(where):
    where_op = where[0]
    where_op_type = where_op[0]
    where_op_type_label = where_op_type.label()
    where_col_val = where[1].leaves()[0]
    op_sign = labelToSign(where_op_type_label)

    where = f"WHERE {where_col_val} {op_sign}"

    if(where_op_type_label == "EQUAL"):
        where += " True"

    return where


def labelToSign(label):
    signs = {
        'ALL' : '*',
        'COUNT' : 'COUNT(*)',
        "EQUAL" : '=',
        "LESS" : '<',
        "MORE" : '>'
    }
    return signs.get(label)

def buildQuery(sent, table):
    parsed = None

    grammar = populateGrammar(sent)
    rd = RecursiveDescentParser(grammar)

    try:
        for p in rd.parse(sent.split()):
            parsed = p
            break
    except:
        return False

    query_string = "SELECT"
    is_single = False
    query = parsed[0]
    query_label = query.label()
    if(query_label == "QUERY_MANY"):
        aggr = query[0]
        aggr_label = aggr[0].label()
        aggr_sign = labelToSign(aggr_label)
        where_query = whereToQuery(query[2])
        query_string += f" {aggr_sign} {where_query}"

    elif(query_label == "QUERY_SINGLE"):
        is_single = True
        aggr = query[1]
        col = query[2]
        aggr_label = aggr[0].label()
        aggr_col_val = col.leaves()[0]
        query_string += f" {aggr_label}({aggr_col_val})"

    query_string += f" FROM {table}"

    if is_single:
        query_string += " LIMIT 1"

    return query_string

table = "people"

with open('sample.txt', 'r') as f:
    for sent in f:
        sent = sent.replace('\n', '')
        print(sent)
        query = buildQuery(sent, table)
        if query:
            print(query)
        else:
            print("Unable to parse sentence")
