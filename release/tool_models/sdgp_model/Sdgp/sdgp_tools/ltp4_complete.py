import sys
from ltp import LTP


def find_key_nodes(graph_data):
    list_of_key_nodes_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] == -1:
            list_of_key_nodes_indexes.append(item[6])
    list_of_key_nodes_indexes = list(set(list_of_key_nodes_indexes))
    return list_of_key_nodes_indexes


def find_key_nodes_dep(graph_data):
    list_of_key_nodes_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] == -1:
            list_of_key_nodes_indexes.append(index)
    return list_of_key_nodes_indexes


def find_key_nodes_sdgp(graph_data):
    list_of_key_nodes_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] == -1:
            list_of_key_nodes_indexes.append(item[4])
    return list_of_key_nodes_indexes


class Ltp4(object):
    def __init__(self, device=None):
        self.device = device
        self.ltp = LTP(path='base', device=self.device)
        # ltp = LTP(path = "base|small|tiny")

    def analyze(self, text, sub_label='', print_info=False, sdp_mode='tree'):
        list_to_return = []
        if print_info:
            print("————————————————————")
            print("当前文本：{}".format(text))

        words, hidden = self.ltp.seg([text])
        postags = self.ltp.pos(hidden)
        arcs = self.ltp.dep(hidden)
        srls = self.ltp.srl(hidden, keep_empty=False)
        sdps = self.ltp.sdp(hidden, mode=sdp_mode)
        if print_info:
            print('语义依存采用', sdp_mode, '结构进行解析')

        words = words[0]
        words_str = '\t'.join(words)
        if print_info:
            print("[分词]")
            print(words_str)

        postags = postags[0]
        postags_str = '\t'.join(postags)
        if print_info:
            print("[词性标注]")
            print(postags_str)

        arcs = arcs[0]
        rely_id = [arc[1] for arc in arcs]
        relations = [arc[2] for arc in arcs]
        if print_info:
            print("[依存句法]")
            print(arcs)

        sdps = sdps[0]
        sdp_word_indexes = [sdp[0] for sdp in sdps]
        sdp_rely_id = [sdp[1] for sdp in sdps]
        sdp_relations = [sdp[2] for sdp in sdps]
        if print_info:
            print("[语义依存]")
            print(sdps)

        srls = srls[0]
        if print_info:
            print("[语义角色标注]")
            print(srls)

        list_to_return.append({
            'sub_label': sub_label,
            'text': text,
            'words': words,
            'postags': postags,
            'heads': rely_id,
            'relations': relations,
            'sdgp_word_indexes': sdp_word_indexes,
            'sdgp_heads': sdp_rely_id,
            'sdgp_relations': sdp_relations,
            'srls': srls,
        })

        return list_to_return

    def entity_separation_dep(self, text):
        words, hidden = self.ltp.seg([text])
        postags = self.ltp.pos(hidden)
        arcs = self.ltp.dep(hidden)
        core_entity = ''
        modifier_part = ''
        words = words[0]
        postags = postags[0]
        arcs = arcs[0]
        heads = [arc[1] for arc in arcs]
        relations = [arc[2] for arc in arcs]

        graph_data = [[token, head, relation, postag] for
                      token, head, relation, postag in
                      zip(words, heads, relations, postags)]
        for index, item in enumerate(graph_data):
            graph_data[index][1] -= 1
        indexes_of_key_tokens = find_key_nodes_dep(graph_data)
        if len(indexes_of_key_tokens) == 0:
            sys.exit()
        index_of_key_token = indexes_of_key_tokens[0]
        core_entity_postag = graph_data[index_of_key_token][3]
        if core_entity_postag == 'n' or core_entity_postag == 'nd' or core_entity_postag == 'nh'\
                or core_entity_postag == 'ni' or core_entity_postag == 'nl' or core_entity_postag == 'ns'\
                or core_entity_postag == 'nt' or core_entity_postag == 'nz' or core_entity_postag == 'pronoun'\
                or core_entity_postag == 'a':
            core_entity = graph_data[index_of_key_token][0]
            modifier_part = ''.join([token[0] for token in graph_data[:index_of_key_token]])

        return core_entity, modifier_part, core_entity_postag

    def entity_separation_sdp(self, text, mode='tree'):
        words, hidden = self.ltp.seg([text])
        postags = self.ltp.pos(hidden)
        sdps = self.ltp.sdp(hidden, mode=mode)
        core_entity = ''
        modifier_part = ''
        words = words[0]
        postags = postags[0]
        sdps = sdps[0]
        sdgp_word_indexes = [sdp[0] for sdp in sdps]
        heads = [sdp[1] for sdp in sdps]
        relations = [sdp[2] for sdp in sdps]
        start_indexes = [index for index, word in enumerate(words)]
        end_indexes = [index for index, word in enumerate(words)]

        graph_data = []
        for sdgp_reword_num, word_index in enumerate(sdgp_word_indexes):
            info_this_reword = [words[word_index - 1], heads[sdgp_reword_num], relations[sdgp_reword_num],
                                postags[word_index - 1],
                                start_indexes[word_index - 1], end_indexes[word_index - 1], word_index]
            graph_data.append(info_this_reword)
        for index, item in enumerate(graph_data):
            graph_data[index][1] -= 1
        for index, item in enumerate(graph_data):
            graph_data[index][6] -= 1
        punctuations_to_remove = ['，', '。', '；', '！', '？', '?', '!', ';']
        for index, item in enumerate(graph_data):
            if item[1] > -2 and item[2] == 'mPUNC' and \
                    item[0] in punctuations_to_remove:
                graph_data[index][1] = -2

        indexes_of_key_tokens = find_key_nodes(graph_data)

        if len(indexes_of_key_tokens) == 0:
            sys.exit()
        index_of_key_token = indexes_of_key_tokens[0]
        core_entity_postag = graph_data[index_of_key_token][3]
        if core_entity_postag == 'n' or core_entity_postag == 'nd' or core_entity_postag == 'nh' \
                or core_entity_postag == 'ni' or core_entity_postag == 'nl' or core_entity_postag == 'ns' \
                or core_entity_postag == 'nt' or core_entity_postag == 'nz' or core_entity_postag == 'pronoun'\
                or core_entity_postag == 'a':
            core_entity = graph_data[index_of_key_token][0]
            modifier_part = ''.join([token[0] for token in graph_data[:index_of_key_token]])

        return core_entity, modifier_part, core_entity_postag

    def sent_split_ltp(self, single_text_span):
        sents = self.ltp.sent_split([single_text_span])
        return sents


def parse_some_sentences():
    pass


if __name__ == '__main__':
    parse_some_sentences()
