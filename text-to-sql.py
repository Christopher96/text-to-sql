import nltk
import mysql.connector
import sys
from nltk.parse.recursivedescent import RecursiveDescentParser
from nltk import CFG

table = "people"

conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="test"
        )

cursor = conn.cursor(buffered=True)

def populateGrammar(sent):
    grammar = readFile("grammar.txt")

    split = sent.split()
    tagged = nltk.pos_tag(split, tagset="universal")
    for i in range(len(split)):
        word, tag = tagged[i]
        # We include all tags in grammar
        grammar += f"{tag} -> '{word}'\n"
        grammar += f"ANY -> '{word}'\n"

    grammar += f"TABLE -> '{table}'\n"

    executeQuery(f"describe {table}")
    results = cursor.fetchall()

    for col in results: 
        col_name = col[0]
        grammar += f"COL -> '{col_name}'\n"


    return CFG.fromstring(grammar)

def queryType(query):
    labels = []
    for node in query:
        labels.append(node.label())

    return " ".join(labels)

def whereToQuery(where):
    query_type = queryType(where)

    op = col = []

    if query_type == "OP COL ANY":
        op, col, noun = where
        col_search = noun.leaves()[0]
    elif query_type == "ANY COL OP NUM":
        any, col, op, num = where
        col_search = num.leaves()[0]

    op_type = op[0]
    op_type_label = op_type.label()
    col_name = col.leaves()[0]
    op_sign = labelToSign(op_type_label)

    query = f" WHERE {col_name} {op_sign}"

    if(col_search != ""):
        query += f" '{col_search}'"
    else:
        query += " True"

    return query


def labelToSign(label):
    signs = {
        'ALL' : '*',
        'COUNT' : 'COUNT(*)',
        "EQUAL" : '=',
        "LESS" : '<',
        "MORE" : '>',
    }
    return signs.get(label)

def buildQuery(sent):
    query = None

    grammar = populateGrammar(sent)
    rd = RecursiveDescentParser(grammar)

    try:
        for p in rd.parse(sent.split()):
            query = p
            break
    except:
        return False

    if not query: return False

    query_type = queryType(query)

    aggr_query = ""
    from_query = f" FROM {table}"
    where_query = ""

    if(query_type == "AGGR TABLE WHERE"):
        aggr, tabl, where = query
        aggr_label = aggr[0].label()
        aggr_sign = labelToSign(aggr_label)
        where_query = whereToQuery(query[2])
        aggr_query = f" {aggr_sign}"
    elif(query_type == "SINGLE AGGR COL"):
        single, aggr, col = query
        aggr_label = aggr[0].label()
        aggr_sign = labelToSign(aggr_label)
        aggr_col_val = col.leaves()[0]
        aggr_query = f" {aggr_label}({aggr_col_val})"

    query_string = "SELECT"
    query_string += aggr_query
    query_string += from_query
    query_string += where_query

    return query_string

def testQuery(query, match):
    if query == match:
        print(f"OK: {query}")
    else:
        print("Query does not match.\n")
        print(f"Got: {query}")
        print(f"Should be: {match}")

def executeQuery(query):
    cursor.execute(query)
    conn.commit()

def printResults():
    results = cursor.fetchall()

    widths = []
    columns = []
    tavnit = '|'
    separator = '+' 

    for cd in cursor.description:
        widths.append(15)
        columns.append(cd[0])

    for w in widths:
        tavnit += " %-"+"%ss |" % (w,)
        separator += '-'*w + '--+'

    print(separator)
    print(tavnit % tuple(columns))
    print(separator)
    for row in results:
        print(tavnit % row)
    print(separator)

def readFile(name):
    f = open(name, "r")
    txt = f.read()
    f.close()
    return txt


def testQuestions():
    sentences = readFile("sentences.txt").split("\n")
    queries = readFile("queries.txt").split("\n")

    for i in range(len(sentences)):
        sent = sentences[i]
        if sent:
            print(f"Parsing: {sent}")
            query = buildQuery(sent)
            if query:
                testQuery(query, queries[i])
            else:
                print("Unable to parse sentence")


def promptQuestion():
    while True:
        try:
            question = input("Ask me something: ").replace("?", "")
            query = buildQuery(question)
            if query:
                print(f"\n{query}")
                executeQuery(query)
                printResults()
                print()
            else:
                print("Unable to parse sentence")
        except KeyboardInterrupt:
            print("Exiting...")
            break

promptQuestion()

conn.close()
sys.exit()
