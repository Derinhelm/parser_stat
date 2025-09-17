import argparse
import pickle
import os
import cProfile
import pstats
import io
import statistics
from collections import OrderedDict

from data_classes import ConllEntry


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
            t = ConllEntry(
                str(token.i + 1),
                form=token.text,
                parent_id=str(parent_id),
                relation=relation,
            )
            res.append(t)
        return res


class StanzaParser:
    def __init__(self):
        import stanza

        self.nlp = stanza.Pipeline(
            lang="ru", processors="tokenize, pos, lemma, depparse"
        )

    def parse(self, sent):
        doc = self.nlp(sent)
        res = []
        for sentence in doc.sentences:
            for word in sentence.words:
                relation = word.deprel
                if relation == "ROOT":
                    relation = "root"
                c = ConllEntry(
                    str(word.id),
                    form=word.text,
                    parent_id=str(word.head),
                    relation=relation,
                )
                res.append(c)
        return res


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
            c = ConllEntry(
                str(token.id[2:]),
                form=token.text,
                parent_id=str(token.head_id[2:]),
                relation=token.rel,
            )
            res.append(c)
        return res


def extract_profiling_fields(stats_output, target_keys):
    profiling_values = {key: [] for key in target_keys}

    for output in stats_output:
        for line in output.splitlines():
            for key in target_keys:
                if key in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            percall = float(parts[3])
                            profiling_values[key].append(percall)
                        except ValueError:
                            continue
    return {k: sum(v) / len(v) if v else 0.0 for k, v in profiling_values.items()}


def profile_f(sent, parser, corpus_name, parser_name, i):
    stats_output = []
    total_times = []

    for run in range(10):
        pr = cProfile.Profile()
        pr.enable()
        _ = parser.parse(sent.text)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()
        stats_output.append(s.getvalue())

        total_time = ps.total_tt
        total_times.append(total_time)

    avg_time = statistics.mean(total_times)

    # configured manually for each parser
    profiling_fields = [
        "trainable_pipe:40:__call__",
        "tok2vec.py:113(predict)",  # Эмбеддинги токенов
        "model.py:330(predict)",  # Предсказание переходов
        "model.py:124(layers)",  # Архитектура модели (CNN/MLP)
        "beam_utils.py:200(collect_states)",  # Beam search: сбор состояний
        "arc_eager.py:750(set_annotations)",  # Применение зависимостей (синтаксический анализ)
        "nonproj.py:176(deprojectivize)",  # Восстановление непроектных дуг
    ]

    profiling_data = extract_profiling_fields(stats_output, profiling_fields)

    return OrderedDict(
        {
            "sent_id": sent.sent_id,
            "total_time": avg_time,
            "profiling_data": profiling_data,
        }
    )


parser = argparse.ArgumentParser(description="Info about parser tests")
parser.add_argument("pickle_data_path", type=str, help="Path to input .pickle")
parser.add_argument(
    "parser_name", choices=["stanza", "spacy", "natasha"]
)
args = parser.parse_args()

with open(args.pickle_data_path, "rb") as f:
    data = pickle.load(f)

parser_dict = {"stanza": StanzaParser, "natasha": NatashaParser, "spacy": SpacyParser}
parser_class = parser_dict[args.parser_name]
parser_instance = parser_class()

profiling_results = OrderedDict()

for treebank_name, treebank_sents in data.items():
    print(f"\nProcessing corpus: {treebank_name}")
    t_res = []
    for i, sent in enumerate(treebank_sents):
        if i % 100 == 0:
            print(f"{i:4}/{len(treebank_sents)}")
        t_res.append(
            profile_f(sent, parser_instance, treebank_name, args.parser_name, i)
        )
    profiling_results[treebank_name] = t_res

output_file = f"{args.parser_name}_profiling_test.pickle"
with open(output_file, "wb") as f:
    pickle.dump(profiling_results, f)
print(f"\nProfiling data saved to: {output_file}")
