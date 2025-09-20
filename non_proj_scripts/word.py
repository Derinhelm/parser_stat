from xml.dom.minidom import Element
from classes.grammar import Grammar
from functions.debug_functions import dbg_print


non_projective = set()
d = {}  # словарь всей грамматики граммема - слова
seen_ids = set()

class Word:
    def __init__(self, w: Element, sentId):
        dom = w.getAttribute('DOM')
        self.dom = int(dom) if dom != '_root' else -1
        self.feat = w.getAttribute('FEAT')
        self.featList = self.feat.replace(' МЕТА', '').replace(' НАСТ ', ' ').replace(' СЛ', '').replace('COM', '')
        self.feat = self.feat.replace(' МЕТА', '').replace(' НАСТ ', ' ').replace(' СЛ', '').replace('COM', '')

        if self.feat == '':
            self.featList = ['S']
            self.feat = 'S'
        else:
            self.featList = self.featList.split(' ')
            self.feat = self.feat.split(' ')[0]

        self.id = int(w.getAttribute('ID'))
        self.lemma = w.getAttribute('LEMMA')
        self.link = w.getAttribute('LINK')

        v = " ".join(t.nodeValue for t in w.childNodes if t.nodeType == t.TEXT_NODE).lower().strip()
        if self.link == 'пасс-анал':
            dbg_print(v)
            dbg_print(f'Sentence={sentId}, Lemma={self.lemma}, id={self.id}')
            pass
        # v - просто слово

        if len(v) != 0 and v[-1] == '.':
            v = v[:-1]
        if v != '':
            # добавление слова в словарь
            if self.feat in d.keys():
                d[self.feat].add(v)
            else:
                d[self.feat] = {v}
        self.v = v
        self.sentId = sentId
        self.connectedWords = []  # связанные с этим словом слова

    def addWord(self, w):
        # добавление слова в связанные с этим словом слова
        #if not self.is_descendant(w): #uncomment if generating json
        self.connectedWords.append(w)

        
    def is_descendant(self, potential_child):
        if potential_child is self:
            return True

        for child in self.connectedWords:
            if child.is_descendant(potential_child):
                return True
        return False
    
    def to_json(self):
        word_dict = {
            "word": self.v,
            "feat": self.featList,
            "link": self.link if self.link != '' else None,
            "order": self.id,
            "children": [child.to_json() for child in self.connectedWords if child != self]
        }
        return word_dict

    def makeNodeName(self, withSSR):
        ssr = (', ' + self.link) if withSSR else ''
        return '$D{' + f'[{self.feat}' + ssr + ']' + '}'

    def generateNode(self, grammar: Grammar, checkProj = True):
        if checkProj:
            global seen_ids
            seen_ids = set()
            if is_non_projective(self):
                non_projective.add(self.sentId)
                return None
        if len(self.connectedWords) > 1:
            # construct grammar for tier
            nodeName = self.makeNodeName(False)
            node = grammar.addNode(nodeName, 'DESCRIPTOR @CheckTier')
            assert (node != None)
            fromState = node.getZeroState()
            i = 1
            for w in self.connectedWords: # проход по всем словам в связанных словах
                if w == self:
                    operators = '@ToMainWord'
                    label = f'[{self.feat}]'
                    toState = node.addNewArc(fromState, f'[{self.feat}]', operators, i == len(self.connectedWords))
                else:
                    operators = '@CopySSR @ToTier'
                    label = w.makeNodeName(True)
                    toState = node.addNewArc(fromState, w.makeNodeName(True), operators,  i == len(self.connectedWords))
                    #now add node for word in tier
                    wordNodeName = w.makeNodeName(True)
                    finalOps =  'DESCRIPTOR @CheckSSRAnyWord'
                    if len(w.connectedWords) <= 1:
                        nodeForTerm = grammar.addNode(wordNodeName, finalOps)
                        operators = f'@ToMainWord @ToSSR("{w.link}")'
                        nodeForTerm.getZeroState().addArc(nodeForTerm.getFinalState().id, f'[{w.feat}]', operators)
                    else:
                        ntNode = grammar.addNode(wordNodeName, finalOps)
                        operators = f'@ToSSR("{w.link}") @CopyMainWord @CopyBonus'
                        ntNode.getZeroState().addArc(ntNode.getFinalState().id, w.makeNodeName(False), operators)
                    w.generateNode(grammar, False)
                i+=1
                fromState = toState
            return node
        else:
            return None

def is_tree_non_proj(sent):
    global seen_ids
    seen_ids = set()
    return is_non_projective(sent.rootWord)
    
def is_non_projective(w):
    for v in [f for f in w.connectedWords if int(f.id) < int(w.id)]:
        t = is_non_projective(v)
        if t:
            return True

    if any(map(lambda x: int(x) > int(w.id), seen_ids)):
        return True
    seen_ids.add(w.id)

    for v in [f for f in w.connectedWords if int(f.id) > int(w.id)]:
        t = is_non_projective(v)
        if t:
            return True

    return False