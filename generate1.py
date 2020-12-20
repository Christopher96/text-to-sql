import nltk.corpus
moby = nltk.corpus.gutenberg.words('melville-moby_dick.txt')
from nltk.text import Text
import re

# Sample sentences to parse
f = open("sample.txt", "r")
sample_text = f.read()
sample_text = re.split(" |\n", sample_text)


sample = Text(moby)
generated = sample.generate()

print(type(moby))
