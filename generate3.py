import nltk
from nltk.tokenize import word_tokenize

sent = 'how many people are male'
tokens = word_tokenize(sent)
tagged_sent = nltk.pos_tag(tokens, tagset='universal')
print(tagged_sent)
