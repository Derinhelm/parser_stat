import argparse
from copy import deepcopy
import pickle
import time

from data_classes import ConllEntry, Sentence

class UDPipeSpacyParser:
    def __init__(self):
        import spacy_udpipe
        spacy_udpipe.download("ru")
        self.udpipe_model = spacy_udpipe.load("ru")

    def parse(self, sent):
        parsed = self.udpipe_model(sent.text)
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


class UDPipeSpacyTokenParser:
    def __init__(self):
        import spacy_udpipe
        spacy_udpipe.download("ru")
        self.udpipe_model = spacy_udpipe.load("ru")

    def parse(self, sent):
        parsed = self.udpipe_model.tokenizer([[t.form for t in sent.tokens if "." not in t.id]])
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
        import nltk
        nltk.download('punkt_tab')
        self.model = build_model('syntax_ru_syntagrus_bert', install=True, download=True)

    def parse(self, sent):
        conll_res = self.model([sent.text])
        res = []
        for word_res in conll_res[0].split('\n'):
            if word_res.strip(): # ignore empty lines
                wr = word_res.split('\t')
                t =  ConllEntry(str(wr[0]), form=wr[1], parent_id=str(wr[6]), relation=wr[7])
                res.append(t)
        return res


class DeepPavlovTokenParser:
    def __init__(self):
        from deeppavlov import build_model
        import nltk
        nltk.download('punkt_tab')
        self.model = build_model('syntax_ru_syntagrus_bert', install=True, download=True)

    def parse(self, sent):
        def conll_tokenizate(params):
            return [[t.form for t in sent.tokens if "." not in t.id]]
        self.model.pipe[0] = (self.model.pipe[0][0],
                              self.model.pipe[0][1], conll_tokenizate)
        conll_res = self.model([sent.text])
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
        parsing_res = self.nlp(sent.text)
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


class SpacyTokenParser:
    def __init__(self):
        import spacy
        self.nlp = spacy.load("ru_core_news_lg")

    def parse(self, sent):
        from spacy.tokens import Doc
        token_doc = Doc(self.nlp.vocab,
                        [t.form for t in sent.tokens if "." not in t.id])
        parsing_res = self.nlp(token_doc)
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
        doc = self.nlp(sent.text)
        res = []
        for sentence in doc.sentences:
            for word in sentence.words:
                relation = word.deprel
                if relation == "ROOT":
                  relation = "root"
                c = ConllEntry(str(word.id), form=word.text, parent_id=str(word.head), relation=relation)
                res.append(c)
        return res


class StanzaTokenParser:
    def __init__(self):
        import stanza
        self.nlp = stanza.Pipeline(lang='ru', processors='tokenize, pos, lemma, depparse')

    def parse(self, sent):
        from stanza.models.common.doc import Document
        def conll_tokenize(document):
            print("conll_tokenize")
            from functions import create_sent_be_nodes
            ideal_tokens = create_sent_be_nodes(sent, lambda text: text.lower().replace("''", '"'))
            res = [[]]
            for (ideal_token, (start, end)) in ideal_tokens[0]:
                    res[0].append({ "text": ideal_token.form
                               , "start_char": start, "end_char": end })
            return Document(res)
        self.nlp.processors['tokenize'].process = lambda t: conll_tokenize(t)
        doc = self.nlp(sent.text)
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
        self.Doc = Doc

    def tokenizate(self, sent, doc):
        doc.segment(self.segmenter)

    def parse(self, sent):
        doc = self.Doc(sent.text)
        self.tokenizate(sent, doc)
        doc.parse_syntax(self.syntax_parser)
        res = []
        for token in doc.tokens:
            c = ConllEntry(str(token.id[2:]), form=token.text, parent_id=str(token.head_id[2:]), relation=token.rel)
            res.append(c)
        return res

class NatashaTokenParser(NatashaParser):
    def tokenizate(self, sent, doc):
        from functions import create_sent_be_nodes
        doc.segment(self.segmenter)
        ideal_tokens = create_sent_be_nodes(sent, lambda text: text.lower().replace("''", '"'))
        #print(doc.tokens, [(token.form, start, end)
        #                   for (token, (start, end)) in ideal_tokens[0]])
        tokens = []
        token_pattern = doc.tokens[0]
        for t_id, (ideal_token, (start, end)) in enumerate(ideal_tokens[0]):
                token = deepcopy(token_pattern)
                token.start = start
                token.stop = end
                token.id = t_id + 1
                token.text = ideal_token.form
                tokens.append(token)
        doc.sents[0].tokens = tokens
        doc.tokens = tokens

parser = argparse.ArgumentParser(description='Info about parser tests')
parser.add_argument('pickle_data_path', type=str, help='Path')
parser.add_argument('parser_name', choices=["stanza", "spacy", "deeppavlov",\
                                            "udpipe", "natasha",
                                            "natasha_t", "spacy_t",
                                            "deeppavlov_t", "stanza_t", "udpipe_t"])
args = parser.parse_args()
print(args.pickle_data_path)
print(args.parser_name)

with open(args.pickle_data_path, 'rb') as f:
    data = pickle.load(f)

parser_dict = { 'udpipe': UDPipeSpacyParser, 'stanza': StanzaParser,\
                'natasha': NatashaParser, 'deeppavlov': DeepPavlovParser,\
                'spacy': SpacyParser, 'spacy_t': SpacyTokenParser,
                'natasha_t': NatashaTokenParser,
                'deeppavlov_t': DeepPavlovTokenParser,
                'stanza_t': StanzaTokenParser, 'udpipe_t': UDPipeSpacyTokenParser}
parser_class = parser_dict[args.parser_name]
parser = parser_class()

res = {}
time_dict = {}
for treebank_name, treebank_sents in data.items():
    t_res = []
    print("\n", treebank_name)
    t_time = []
    for i, sent in enumerate(treebank_sents):
        if i % 100 == 0:
            print(f"{i:4}/{len(treebank_sents)}")
        ts = time.time()
        token_list = parser.parse(sent)
        te = time.time()
        t_time.append(te - ts)
        cur_res = Sentence()
        cur_res.set_sent_id(sent.sent_id)
        cur_res.set_text(sent.text)
        for t in token_list:
            cur_res.add_token(t)
        t_res.append(cur_res)
    res[treebank_name] = t_res
    time_dict[treebank_name] = sum(t_time)

print("\ntime results (s):")
for p, t in time_dict.items():
    print(f"{p:10}: {t:5.3f} (s)")

with open(f'{args.parser_name}.pickle', 'wb') as f:
    pickle.dump(res, f)
    
    

