import math
import fractions

class WordStat:
    doccount = 1
    stnum = fractions.Fraction(0)
    stden = fractions.Fraction(0)

    def get_score(self):
        if self.stden == 0:
            return 0.0
        return float(self.stnum / self.stden)

class DocStat:
    rating = 0

    def __init__(self, wordlist):
        count = {}
        for word in wordlist:
            count[word] = count.get(word, 0) + 1
        self.hist = list(count.items()) # This is ok for both py2 and py3.
        self.length = len(wordlist)

    def rate(self, r):
        self.rating = r

class Knowledge:
    vocab = {}
    length = 0

    def birth(self, docstat):
        self.length += 1
        sdnum = fractions.Fraction(0)
        sdden = fractions.Fraction(0)
        for word, count in docstat.hist:
            if word not in self.vocab:
                self.vocab[word] = WordStat()
            else:
                self.vocab[word].doccount += 1
            idf = math.log10(self.length / self.vocab[word].doccount)
            w = count * idf
            sdnum += self.vocab[word].get_score() * w
            sdden += w
        if sdden == 0:
            return 0.0
        return float(sdnum / sdden)

    def death(self, docstat):
        for word, count in docstat.hist:
            tf = fractions.Fraction(count, docstat.length)
            self.vocab[word].stnum += docstat.rating * tf
            self.vocab[word].stden += tf

if __name__ == "__main__":
    knowledge = Knowledge()
    wls = [
      ['a', 'b', 'c', 'b'],
      ['d', 'c', 'b', 'b'],
      ['a', 'c', 'd', 'a', 'd'],
      ['e', 'c', 'c', 'b']
    ]
    rs = [-10, +20, +30, -30]
    docs = [DocStat(wl) for wl in wls]
    for doc, r in zip(docs, rs):
        s = knowledge.birth(doc)
        doc.rate(r)
        print(s)

    for doc in docs:
        knowledge.death(doc)
    print("")

    for doc in docs:
        s = knowledge.birth(doc)
        print(s)
