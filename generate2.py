import nltk
from nltk import CFG
from nltk.parse.generate import generate, demo_grammar

grammar = CFG.fromstring("""
S -> NP VP
PP -> P NP
NP -> Det N | Det N PP
VP -> V NP | VP PP
Det -> 'a' | 'A'
N -> 'car' | 'door'
V -> 'has'
P -> 'in' | 'for'
""")

parser = nltk.ChartParser(grammar)

# Tokenize by words in sentences
words = nltk.word_tokenize("A car has a door")

for sentence in generate(grammar, n=3):
    print(' '.join(sentence))

# print(trees.generate())
