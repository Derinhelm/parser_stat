import argparse
import pickle
import time

from data_classes import ConllEntry, Sentence


class NatashaEmbedder:
    def __init__(self):
        from natasha import Segmenter, NewsEmbedding, NewsSyntaxParser, Doc
        emb = NewsEmbedding()
        self.segmenter = Segmenter()
        self.syntax_parser = NewsSyntaxParser(emb)
        self.Doc = Doc

    def is_unk(self, t_id):
        return bool(t_id == self.syntax_parser.infer.encoder.words_vocab.unk_id)
        
    def is_pad(self, t_id):
        return bool(t_id == self.syntax_parser.infer.encoder.words_vocab.pad_id)

    def get_shape(self, shape_id):
        return self.syntax_parser.infer.encoder.shapes_vocab.decode(shape_id)

    def parse(self, sent):
        doc = self.Doc(sent)
        doc.segment(self.segmenter)
        emb_res = list(self.syntax_parser.infer.encoder([[t.text for t in s.tokens] for s in doc.sents]))
        assert len(emb_res) == 1
        res = []
        assert len(emb_res[0].word_id) == len(emb_res[0].shape_id)
        for subsent_i, subsent_token_ids in enumerate(emb_res[0].word_id):
        # Тестовое предложение может быть разделено на несколько предложений
        # каждое обрабатываем отдельно, результаты объединяем.
            subsent_shape_ids = emb_res[0].shape_id[subsent_i]
            assert len(subsent_token_ids) == len(subsent_shape_ids)
            for t_i, token_id in enumerate(subsent_token_ids):
                if not self.is_pad(token_id):
                    shape_id = subsent_shape_ids[t_i]
                    token_is_unk = self.is_unk(token_id)
                    token_shape = self.get_shape(shape_id)
                    res.append((token_is_unk, token_shape))
        return res

parser = argparse.ArgumentParser(description='Info about parser tests')
parser.add_argument('pickle_data_path', type=str, help='Path')
args = parser.parse_args()
print(args.pickle_data_path)

with open(args.pickle_data_path, 'rb') as f:
    data = pickle.load(f)

parser = NatashaEmbedder()

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
        t_res.append(token_list)
    res[treebank_name] = t_res
    time_dict[treebank_name] = sum(t_time)

print("\ntime results (s):")
for p, t in time_dict.items():
    print(f"{p:10}: {t:5.3f} (s)")

with open('pickle_results/natasha_emb.pickle', 'wb') as f:
    pickle.dump(res, f)

