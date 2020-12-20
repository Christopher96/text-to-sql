import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from nltk import CFG
from nltk.parse.generate import generate, demo_grammar
from collections import defaultdict

# Training corpora
train_text = state_union.raw("2005-GWBush.txt")

# Sample sentences to parse
f = open("sample.txt", "r")
sample_text = f.read()

# Sample sentences to parse
f = open("custom.txt", "r")
custom_text = f.read()

# Use the PunktSentenceTokenizer and train it with our corpora
custom_sent_tokenizer = PunktSentenceTokenizer(train_text)


def parse_and_generate(text):
    # Tokenize sentences
    sentences = custom_sent_tokenizer.tokenize(text)

    try:
        cfgstring = """
        S  -> NP VP | S CONJ S
        NP -> DET N
        NOM -> ADJ N
        VP -> V ADJ | V NP | V S | V NP PP
        PP -> P NP
        N -> NOUN
        V -> VERB
        """

        tag_dict = defaultdict(list)

        for sent in sentences:
            # Tokenize by words in sentences
            tokens = nltk.word_tokenize(sent)

            # Tag the words
            tagged_sent = nltk.pos_tag(tokens, tagset='universal')

            print(tagged_sent)

            # Put tags and words into the dictionary
            for word, tag in tagged_sent:
                if(tag == "."):
                    continue
                if tag not in tag_dict:
                    tag_dict[tag].append(word.lower())
                elif word not in tag_dict.get(tag):
                    tag_dict[tag].append(word.lower())

        for tag, words in tag_dict.items():
            cfgstring += tag + " -> "
            first_word = True
            for word in words:
                if first_word:
                    cfgstring += "\"" + word + "\""
                    first_word = False
                else:
                    cfgstring += " | \"" + word + "\""
            cfgstring += "\n"

        grammar = CFG.fromstring(cfgstring)

        for sentence in generate(grammar, n=10, depth=8):
            print(' '.join(sentence))

    except Exception as e:
        print(str(e))

parse_and_generate(custom_text)


