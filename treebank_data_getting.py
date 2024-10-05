import pickle

from data_classes import ConllEntry, Sentence

def get_dataset_sentences(dataset_path):
    fh = open(dataset_path,'r',encoding='utf-8')
    sents_read = 0
    sents = []
    comments = set()

    sent = Sentence()
    for line in fh:
        tok = line.strip().split('\t')
        if not tok or line.strip() == '': # empty line, add sentence to list
            if sent.is_not_empty:
                sents_read += 1
                sents.append(sent)
            sent = Sentence()
        else:
            if line[0] == '#' or '-' in tok[0]: # a comment line
                line = line.strip()
                if line[:12] == "# sent_id = ":
                    sent.set_sent_id(line[12:])
                elif line[:9] == "# text = ":
                    sent.set_text(line[9:])
                else:
                    comments.add(line)

            else: # an actual ConllEntry, add to tokens
                if tok[2] == "_":
                    tok[2] = tok[1].lower()

                word = ConllEntry(*tok)
                sent.add_token(word)
    fh.close()
    return sents


sents = {}
for treebank_name in ['gsd', 'pud', 'syntagrus', 'poetry', 'taiga']:
    sents[treebank_name] = get_dataset_sentences(f"./treebank_test_sets/ru_{treebank_name}-ud-test.conllu")
    print(treebank_name, len(sents[treebank_name]))

with open(f'./treebank_test_sets/treebank_data.pickle', 'wb') as f:
    pickle.dump(sents, f)
