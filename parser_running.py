import argparse
import pickle

from data_classes import ConllEntry, Sentence

class UDPipeSpacyParser:
    def __init__(self):
        import spacy_udpipe
        spacy_udpipe.download("ru")
        self.udpipe_model = spacy_udpipe.load("ru")

    def parse(self, sent):
        parsed = self.udpipe_model(sent)
        res = []
        for token in parsed:
            if token.dep_ != 'ROOT':
              parent_id = token.head.i+1
              relation = token.dep_
            else:
              parent_id = 0
              relation = 'root'
            c = ConllEntry(str(token.i+1), form=token.text,
                                   parent_id=str(parent_id), relation=relation)
            res.append(c)
        return res


class DeepPavlovParser:
    def __init__(self):
        from deeppavlov import build_model
        self.model = build_model('syntax_ru_syntagrus_bert', install=True, download=True)

    def parse(self, sent):
        conll_res = self.model([sent])
        res = []
        for word_res in conll_res[0].split('\n'):
            if word_res.strip(): # ignore empty lines
                wr = word_res.split('\t')
                t =  ConllEntry(str(wr[0]), form=wr[1], parent_id=str(wr[6]), relation=wr[7])
                res.append(t)
        return res


class SpacyParser:
    def __init__(self):
        import spacy
        self.nlp = spacy.load("ru_core_news_lg")

    def parse(self, sent):
        parsing_res = self.nlp(sent)
        res = []
        for token in parsing_res:
          if token.dep_ == "ROOT":
            parent_id = 0
            relation = "root"
          else:
            parent_id = token.head.i + 1
            relation = token.dep_
          t =  ConllEntry(str(token.i + 1), form=token.text, parent_id=str(parent_id), relation=relation)
          res.append(t)
        return res


class StanzaParser:
    def __init__(self):
        import stanza
        self.nlp = stanza.Pipeline(lang='ru', processors='tokenize, pos, lemma, depparse')

    def parse(self, sent):
        doc = self.nlp(sent)
        res = []
        for sentence in doc.sentences:
            for word in sentence.words:
                relation = word.deprel
                if relation == "ROOT":
                  relation = "root"
                c = ConllEntry(str(word.id), form=word.text, parent_id=str(word.head), relation=relation)
                res.append(c)
        return res


class NatashaParser:
    def __init__(self):
        from natasha import Segmenter, NewsEmbedding, NewsSyntaxParser, Doc
        emb = NewsEmbedding()
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(emb)

    def parse(self, sent):
        doc = Doc(sent)
        doc.segment(self.segmenter)
        doc.parse_syntax(self.syntax_parser)
        res = []
        for token in doc.tokens:
            c = ConllEntry(str(token.id[2:]), form=token.text, parent_id=str(token.head_id[2:]), relation=token.rel)
            res.append(c)
        return res


parser = argparse.ArgumentParser(description='Info about parser tests')
parser.add_argument('pickle_data_path', type=str, help='Path')
parser.add_argument('parser_name', choices=["stanza", "spacy", "deeppavlov",\
                                            "udpipe", "natasha"])
args = parser.parse_args()
print(args.pickle_data_path)
print(args.parser_name)

with open(args.pickle_data_path, 'rb') as f:
    data = pickle.load(f)

parser_dict = {'udpipe': UDPipeSpacyParser, 'stanza': StanzaParser,\
               'natasha': NatashaParser, 'deeppavlov': DeepPavlovParser,\
               'spacy': SpacyParser}
parser_class = parser_dict[args.parser_name]
parser = parser_class()

res = {}
for treebank_name, treebank_sents in data.items():
    t_res = []
    for i, sent in enumerate(treebank_sents):
        if i % 100 == 0:
            print(i)
        token_list = parser.parse(sent.text)
        cur_res = Sentence()
        cur_res.set_sent_id(sent.sent_id)
        cur_res.set_text(sent.text)
        for t in token_list:
            cur_res.add_token(t)
        t_res.append(cur_res)
    res[treebank_name] = t_res
    
with open(f'{args.parser_name}.pickle', 'wb') as f:
    pickle.dump(res, f)
    
    

