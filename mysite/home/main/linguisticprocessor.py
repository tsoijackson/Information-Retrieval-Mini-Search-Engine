from typing import Iterable
from nltk.stem import *

# This will be a linguistic Processor that will take in a LIST or SET or words
# that need to be processed. The class can return set or list depending on the
# format it took in initially.
class LinguisticProcessor():
    def __init__(self, text: Iterable[str]):
        self.text = list(text)

    def process(self):
        self.lowercase()
        self.stemming()
        return self.text

    def lowercase(self):
        for n,word in enumerate(self.text):
            self.text[n] = word.lower()

    def stemming(self):
        stemmer = PorterStemmer()
        for n, word in enumerate(self.text):
            self.text[n] = stemmer.stem(word)

def test():
    l1 = ['Cars', 'Are', 'Super', 'Fast', 'In', 'Cities', 'Citi', 'City', 'Computer', 'Computers', 'fairy', 'fairies']
    s1 = set(l1)

    print("l1:", l1, ',s1:', s1)
    print("l1:", LinguisticProcessor(l1).process(), ',s1:', LinguisticProcessor(s1).process())

if __name__ == '__main__':
    test()