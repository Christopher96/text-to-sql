import nltk
import mysql.connector
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

def populateGrammar(sent, table):
    f = open("grammar.txt", "r")
    grammar = f.read()
    f.close()

    split = sent.split()
    tagged = nltk.pos_tag(split, tagset="universal")
    for i in range(len(split)):
        word, tag = tagged[i]
        # Tags we want to include in the grammar
        if tag in ["NUM"]:
            grammar += f"{tag} -> '{word}'\n"

    grammar += f"TABLE -> '{table}'"

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

    grammar = populateGrammar(sent, table)
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
        widths.append(max(5, len(cd[0])))
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


f = open("sentences.txt", "r")
sentences = f.read().split("\n")
f = open("queries.txt", "r")
queries = f.read().split("\n")
f = open(f"{table}.sql", "r")
table_dump = f.read()
f.close()

executeQuery("SELECT * FROM people")
printResults()

for i in range(len(sentences)):
    break
    sent = sentences[i]
    if sent:
        print(f"Parsing: {sent}")
        query = buildQuery(sent, table)
        print(query)
        executeQuery(query)
        printResults()
        if query:
            print(query)
            # testQuery(query, queries[i])
        else:
            print("Unable to parse sentence")


conn.close()
