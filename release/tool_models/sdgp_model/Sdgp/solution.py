import sys
from typing import List, Dict

from sdgp_tools.ltp4_complete import Ltp4
from sdgp_tools.pruning_and_fusion_ltp4 import node_fusion_for_single_graph_sdgp


def text_type_judgement_kh(subject, object_text, predicate):
    list_of_action_indicators = ['用户']

    for action_indicator in list_of_action_indicators:
        if action_indicator in subject or action_indicator in object_text:
            return 'action'

    if len(subject) == 0:
        return 'action'

    return 'attribute'


def text_type_judgement_kt(subject, object_text, predicate, text_for_agt, text_for_exp):
    if len(subject) == 0:
        return 'action'

    if len(text_for_exp) > 0:
        return 'attribute'
    else:
        return 'action'


def convert_results(items_extracted_sdgp, boundary_strategy):
    processed_results = []
    for item in items_extracted_sdgp:
        subject = item['agent']
        object_text = item['patient']
        predicate = item['predicate']
        text_for_agt = item['text_for_agt']
        text_for_exp = item['text_for_exp']
        if boundary_strategy == 'kh':
            text_type = text_type_judgement_kh(subject, object_text, predicate)
        elif boundary_strategy == 'kt':
            text_type = text_type_judgement_kt(subject, object_text, predicate, text_for_agt, text_for_exp)
        else:
            print('error! unknown boundary strategy:', boundary_strategy)
            sys.exit(1)

        processed_results.append({
            'predicate': item['predicate'],
            'subject': item['agent'],
            'object': item['patient'],
            'time': item['time'],
            'location': item['loc'],
            'manner': item['mann'],
            'reason': item['reas'],
            'negation': item['negation'],
            'relation': item['relation'],
            'attachment': item['attachment'],
            'text_type': text_type,

            'predicate_index_start': item['predicate_index_start'],
            'predicate_index_end': item['predicate_index_end'],
            'text': item['text'],

            'sent_char_start_index': item['sent_char_start_index'],
            'sent_char_end_index': item['sent_char_end_index'],
            'op_start_char_index': item['op_start_char_index'],
            'op_end_char_index': item['op_end_char_index'],
        })

    return processed_results


class SdgpSolution(object):
    def __init__(self, boundary_strategy='kh', device=None):
        self.device = device
        self.ltp_tool = Ltp4(self.device)
        self.boundary_strategy = boundary_strategy

    def extract(self, text_input):
        ltp_out = self.ltp_tool.analyze(text_input, '', False, 'mix')[0]
        items_extracted_sdgp = node_fusion_for_single_graph_sdgp(
            ltp_out, '', '', '', {}, {})
        extraction_results = convert_results(items_extracted_sdgp, self.boundary_strategy)

        return extraction_results

    def predicts(self, source_sentences: List) -> List[Dict]:
        results = []
        for sentence in source_sentences:
            items_extracted_fusion = self.extract(sentence)
            results.append({
                'sentence': sentence,
                'label': items_extracted_fusion,
            })

        return results

    def keywords_extraction(self, text_input):
        keywords = []
        extraction_results = self.extract(text_input)
        for extraction_result in extraction_results:
            for arg in ['subject', 'object', 'time', 'location', 'manner', 'reason']:
                arg_text = extraction_result[arg]
                if len(arg_text) > 0:
                    core_entity, modifier_part, core_entity_postag = self.ltp_tool.entity_separation_dep(arg_text)
                    if len(core_entity) > 0:
                        keywords.append(core_entity)
                    else:
                        core_entity, modifier_part, core_entity_postag = self.ltp_tool.entity_separation_sdp(arg_text, 'mix')
                        if len(core_entity) > 0:
                            keywords.append(core_entity)
        return keywords

    def sent_split_ltp(self, single_text_span):
        sents = self.ltp_tool.sent_split_ltp(single_text_span)
        return sents


if __name__ == '__main__':
    pass
