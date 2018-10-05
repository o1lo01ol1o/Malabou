# -*- coding: utf-8 -*-
import numpy as np
import os
import sys
import re


sys.path.append("../../")
from utils import TextLoader, standardSentenceProcessing, id
LOCAL_PATH = os.path.dirname(__file__)


def dropBracketedTransliteration(xs):
    regex = re.compile("\[(.*?)\]")
    result = re.sub(regex, "", xs)
    return result


class First(TextLoader):
    def __init__(self):
        super().__init__(LOCAL_PATH,
                         "7 _ Is Science the Subject of Philosophy.txt")

    def processText(self):
        _txt = self._load()
        paras = list(filter(lambda x: (x != "") and (
            x != "*"), _txt.split("\n")))[3:-43]
        return [standardSentenceProcessing(dropBracketedTransliteration(x)) for x in paras]

    def yieldParagraphs(self):
        return map(id, self.processText())


def allLoaders():
    l = []
    l.append(First())
    return l


if __name__ == "__main__":
    print(list(First().yieldParagraphs()))
