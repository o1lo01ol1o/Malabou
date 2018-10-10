# -*- coding: utf-8 -*-
import numpy as np
import os
import sys
import re
from parsec import *

sys.path.append("../../")
from utils import TextLoader, standardSentenceProcessing, id
from Lexer import *

LOCAL_PATH = os.path.dirname(__file__)

AUTHOR="Malabou"

def dropBracketedTransliteration(xs):
    regex = re.compile("\[(.*?)\]")
    result = re.sub(regex, "", xs)
    return result


class First(TextLoader):
    def __init__(self):
        super().__init__(LOCAL_PATH,
                         "7 _ Is Science the Subject of Philosophy.txt",
                         "Is Science the Subject of Philosophy",
                         AUTHOR)

    def processText(self):
        (title, author, _txt) = self._load()
        paras = list(filter(lambda x: (x != "") and (
            x != "*"), _txt.split("\n")))[3:-43]
        return (title, author, [standardSentenceProcessing(dropBracketedTransliteration(x)) for x in paras])

    def yieldParagraphs(self):
        return map(id, self.processText())

class Second(TextLoader):
    def __init__(self):
        super().__init__(LOCAL_PATH,
                         "19 _ Repetition revenge plasticity.txt",
                         "Repetition revenge plasticity",
                         AUTHOR)

    def processText(self):
        (title, author, _txt) = self._load()
        paras = list(filter(lambda x: (x != "") and (
            x != "*"), _txt.split("\n")))[3:-5]
        return (title, author, [standardSentenceProcessing(dropBracketedTransliteration(x))for x in paras])

    def yieldParagraphs(self):
        return map(id, self.processText())


class Third(TextLoader):
    def __init__(self):
        super().__init__(LOCAL_PATH,
                         "23 _ Are there still traces.txt",
                         "Are there still traces",
                         AUTHOR)
        self.mkParser()

    def mkParser(self):

        self.parser = many((nonBracked() ^ ((ellipses ^ maybeCitation ^ parenthetical.parsecmap(lambda x: "(" + x.strip() + ") ") )| bracketed.result(""))))

    def processText(self):
        (title, author, _txt) = self._load()
        _txt = ''.join(self.parser.parse(_txt))
        print(_txt)
        paras = list(filter(lambda x: (x != ""), _txt.split("\n")))# [2:]
        return (title, author, [standardSentenceProcessing(x)for x in paras])

    def yieldParagraphs(self):
        return map(id, self.processText())

def allLoaders():
    l = []
    l.append(First())
    l.append(Second())
    l.append(Third())
    return l


if __name__ == "__main__":
    v = list(Third().yieldParagraphs())
    # print(list(v))
