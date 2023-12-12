import sys
import tqdm

from tool_models.sdgp_model.Sdgp.solution import SdgpSolution
from tool_models.sdgp_model.Sdgp.sdgp_tools.ltp4_complete import Ltp4
from similarity.fasttext import FastTextTool
from tools.graph_bulid import build_graph_data_for_reasoning
from tools.question2graph import construct_entity_taxonomy, construct_action_taxonomy
from tools.find_answer import find_answer_for_question


class GraphMatchQA(object):
    def __init__(self, data_from_label, all_documents_info, sp_entities, parsing_model='Sdgp'):
        self.is_label = data_from_label
        self.graph_data_source = all_documents_info
        self.sp_entities = sp_entities
        self.parsing_model = parsing_model
        self.parsing_tool = None
        self.load_parsing_model()
        self.ltp_tool = Ltp4()
        self.reason_graph_all_documents = build_graph_data_for_reasoning(self.graph_data_source, self.is_label)
        self.similarity_tool = FastTextTool()

    def load_parsing_model(self):
        if self.parsing_model == 'Sdgp':
            self.parsing_tool = SdgpSolution()
        else:
            print('model not found:', self.parsing_model)
            sys.exit(1)

    def single_question_type_classification(self, extraction_item):
        question_type = None

        sentence = extraction_item['sentence']
        predicate = extraction_item['predicate']
        subject = extraction_item['subject']
        object_text = extraction_item['object']
        negation = extraction_item['negation']
        text_type = extraction_item['text_type']

        if text_type == 'attribute':
            question_type = 'declarative'
        else:
            question_type = 'procedure'

        return question_type

    def single_predict(self, question, document_id, debug=False, show_parsing=False, show_reasoning_path=False,
                       match_score_threshold=0):
        """
        :return:
        """
        document_id = int(document_id)

        extraction_results = self.parsing_tool.extract(question)
        if len(extraction_results) == 1:
            extraction_item = extraction_results[0]
        elif len(extraction_results) > 1:
            extraction_item = extraction_results[0]
        else:
            return [], 'no type', {}

        if show_parsing:
            print('extraction_item:\n', extraction_item)

        entity_taxonomy = construct_entity_taxonomy(extraction_item, self.sp_entities, self.ltp_tool)
        action_taxonomy = construct_action_taxonomy(extraction_item, self.sp_entities)
        question_type = self.single_question_type_classification(extraction_item)

        question_parsing = {
            'question': question,
            'question_type': question_type,
            'entity_taxonomy': entity_taxonomy,
            'action_taxonomy': action_taxonomy,
            'extraction_item': extraction_item,
        }

        answers, question_type, match_score, info_dict = find_answer_for_question(question_parsing,
                                                                                  self.reason_graph_all_documents,
                                                                                  document_id, question,
                                                                                  match_score_threshold,
                                                                                  self.similarity_tool, debug,
                                                                                  show_reasoning_path)
        info_dict['match_score'] = match_score
        return answers, question_type, info_dict


if __name__ == '__main__':
    pass
