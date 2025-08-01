import argparse
import pickle
import time

from data_classes import ConllEntry, Sentence


class NatashaParser:
    def __init__(self):
        from natasha import Segmenter, NewsEmbedding, NewsSyntaxParser, Doc
        emb = NewsEmbedding()
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(emb)
        self.Doc = Doc

    def parse(self, sent):
        doc = self.Doc(sent)
        doc.segment(self.segmenter)
        doc.parse_syntax(self.syntax_parser)
        res = []
        for token in doc.tokens:
            c = ConllEntry(str(token.id[2:]), form=token.text, parent_id=str(token.head_id[2:]), relation=token.rel)
            res.append(c)
        return res


parser = argparse.ArgumentParser(description='Info about parser tests')
parser.add_argument('pickle_data_path', type=str, help='Path')
parser.add_argument('parser_name', choices=["natasha"])
args = parser.parse_args()
print(args.pickle_data_path)
print(args.parser_name)

with open(args.pickle_data_path, 'rb') as f:
    data = pickle.load(f)

parser_dict = { 'natasha': NatashaParser }
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
        token_list = parser.parse(sent.text)
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
    
    

