import sys
from reasoning import answer_for_procedure, answer_for_declarative


def check_graph_data(reason_graph_document):
    links = reason_graph_document['links']
    if len(links) == 0:
        print('warning: links is empty!!!')
    product_descriptions_attrs = reason_graph_document['product_descriptions_attrs']
    user_constraints_attrs = reason_graph_document['user_constraints_attrs']
    if len(product_descriptions_attrs) == 0 and len(user_constraints_attrs) == 0:
        print('warning: attrs is empty!!!')


def output_graph(reason_graph_document):
    product_descriptions_attrs = reason_graph_document['product_descriptions_attrs']
    user_constraints_attrs = reason_graph_document['user_constraints_attrs']
    for entity_node in product_descriptions_attrs:
        for attr in entity_node['tuples']:
            print(attr)
    for entity_node in user_constraints_attrs:
        for attr in entity_node['tuples']:
            print(attr)
    links = reason_graph_document['links']
    print('links:')
    for link in links:
        print(link)


def deal_single_predicate(question_parsing, reason_graph_document, question, similarity_tool, match_score_threshold,
                          debug, show_reasoning_path):
    question_type = question_parsing['question_type']
    entity_taxonomy = question_parsing['entity_taxonomy']
    action_taxonomy = question_parsing['action_taxonomy']
    extraction_item = question_parsing['extraction_item']
    question_text = question_parsing['question']
    source_sentences = reason_graph_document['source_sentences']

    reason_paths = []
    info_dict = {
        'factoid_style': False,
        'procedure_style': False,
        'inconsistent': False,
        'matched': False,
    }

    if question_type == 'procedure':
        answers, match_score = answer_for_procedure(question_text, source_sentences, extraction_item,
                                                    entity_taxonomy, action_taxonomy, similarity_tool,
                                                    reason_graph_document, match_score_threshold,
                                                    reason_paths, info_dict, debug, top_k=5)
    elif question_type == 'declarative':
        answers, match_score = answer_for_declarative(extraction_item, entity_taxonomy, action_taxonomy,
                                                      reason_graph_document, match_score_threshold, similarity_tool,
                                                      reason_paths, info_dict, debug, top_k=2)
        info_dict['factoid_style'] = True
    else:
        sys.exit(1)

    if len(answers) == 0 and (question_type == 'procedure' or question_type == 'declarative'):
        if question_type == 'procedure':
            answers, match_score = answer_for_declarative(extraction_item, entity_taxonomy, action_taxonomy,
                                                          reason_graph_document, match_score_threshold, similarity_tool,
                                                          reason_paths, info_dict, debug, top_k=2)
        elif question_type == 'declarative':
            answers, match_score = answer_for_procedure(question_text, source_sentences, extraction_item,
                                                        entity_taxonomy, action_taxonomy, similarity_tool,
                                                        reason_graph_document, match_score_threshold,
                                                        reason_paths, info_dict, debug, top_k=5)
    if match_score >= 0:
        info_dict['matched'] = True
    if show_reasoning_path and len(answers) > 0:
        print('reasoning_paths：')
        for reason_path in reason_paths:
            print(reason_path)

    return answers, question_type, match_score, info_dict


def find_answer_for_question(question_parsing, reason_graph_all_documents, document_id, question, match_score_threshold,
                             similarity_tool, debug, show_reasoning_path):
    if document_id in reason_graph_all_documents:
        reason_graph_document = reason_graph_all_documents[document_id]
        # print(reason_graph_document)
    else:
        print('error: document_id not in reason_graph_all_documents:', document_id)
        sys.exit(1)

    answers, question_type, match_score, info_dict = deal_single_predicate(question_parsing, reason_graph_document,
                                                                           question, similarity_tool,
                                                                           match_score_threshold,
                                                                           debug, show_reasoning_path)
    answers = list(set(answers))
    return answers, question_type, match_score, info_dict
