from xml.dom.minidom import Element
from classes.word import Word
from classes.grammar import Grammar

class Sentence:
    def __init__(self, sent: Element):
        self.id = sent.getAttribute('ID')
        self.words = []

        self.parseWords(sent.getElementsByTagName('W'))
        # получаем все элементы xml с тегом W (слова)
        
    def getStr(self):
        res = ''
        for word in self.words:
            res += f'{word.v} '
        return res.strip()

    def parseWords(self, rawWords):

        self.wordMap = {}  # для последующего связывания слов
        # ключ - доминатор(айди доминатора) этого слова
        # значение - список слов, для которых доминатор равен ключу

        for rawWord in rawWords:

            word = Word(rawWord, self.id)  # переносим в класс

            self.words.append(word)  # добавляем в общий список слов

            if word.dom == -1:
                self.rootWord = word  # корневое слово


            # добавление в мапу
            if word.dom in self.wordMap.keys():
                self.wordMap[word.dom].append(word)
            else:
                self.wordMap[int(word.dom)] = [word]
            # добавляем себя в нужном порядке
            if word.id in self.wordMap.keys():
                self.wordMap[word.id].append(word)
            else:
                self.wordMap[word.id] = [word]

        # цикл по всем словам, чтобы связать их с помощью мапы
        for word in self.words:
            if word.id in self.wordMap.keys():
                for d in self.wordMap[word.id]:
                    word.addWord(d)

    def generateNode(self, grammar: Grammar):
        # генерация узла грамматики для корневого слова
        rootNode = self.rootWord.generateNode(grammar)
        if rootNode != None:
            grammar.addRootNode(rootNode)