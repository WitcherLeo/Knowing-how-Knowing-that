import sys
from typing import List


def entities_match_argument(entities: List, argument):
    for entity in entities:
        if entity in argument:
            return True
    return False


def entity_match_each_other(entity1, entity2):
    if entity1 in entity2 or entity2 in entity1:
        return True
    return False


def action_match_each_other(action1, action2):
    if action1 in action2 or action2 in action1:
        return True
    return False


def answer_for_procedure(question_text, source_sentences, extraction_item, entity_taxonomy, action_taxonomy,
                         similarity_tool, reason_graph_document,
                         match_score_threshold,
                         reason_paths, info_dict, debug, top_k=5):
    question_core_action = action_taxonomy['action']
    question_core_entities = []
    for argument in ['subject', 'object']:
        if len(action_taxonomy[argument]['text']) > 0:
            if len(action_taxonomy[argument]['entity']) > 0:
                question_core_entities.append(action_taxonomy[argument]['entity'])
    if debug:
        print('question_core_action: ', question_core_action)
        print('question_core_entities: ', question_core_entities)

    answers = []
    answers_argument, match_score = find_check_list_for_single_question_parsing(question_text, source_sentences,
                                                                                extraction_item,
                                                                                entity_taxonomy,
                                                                                action_taxonomy,
                                                                                reason_graph_document, reason_paths,
                                                                                similarity_tool, info_dict,
                                                                                match_score_threshold,
                                                                                top_k=top_k)
    answers += answers_argument

    return answers[:top_k], match_score


def action_match(sentence, action_predicate, question_core_action, question_core_entities, entity_match):
    matched = False
    matched_entity = None
    if not entity_match:
        if question_core_action in action_predicate or action_predicate in question_core_action:
            matched = True
    else:
        if question_core_action in action_predicate or action_predicate in question_core_action:
            for question_core_entity in question_core_entities:
                if question_core_entity in sentence:
                    matched = True
                    matched_entity = question_core_entity
                    break
    return matched, matched_entity


def find_user_role_restriction(reason_graph_document, reason_paths, top_k=2):
    answers = []
    user_constraints_attrs = reason_graph_document['user_constraints_attrs']
    for user_constraints_attr_item in user_constraints_attrs:
        for user_constraints_attr in user_constraints_attr_item['tuples']:
            if ('用户' in user_constraints_attr['entity']['node_text'] and '限' in user_constraints_attr['action']) \
                    or (
                    '用户' in user_constraints_attr['entity']['node_text'] and '参与' in user_constraints_attr['sentence']):
                answers.append(user_constraints_attr['sentence'])
                reason_paths.append('user_constraint:{}'.format(user_constraints_attr['sentence']))
    return answers[:top_k]


def find_tuple_of_specific_entity(reason_graph_document, entity, top_k=1):
    answers = []
    product_descriptions_attrs = reason_graph_document['product_descriptions_attrs']
    user_constraints_attrs = reason_graph_document['user_constraints_attrs']
    for entity_node in product_descriptions_attrs:
        for attr in entity_node['tuples']:
            if len(attr['attribute']['node_text']) > 0:
                if attr['attribute']['node_text'] in entity:
                    answers.append([attr['sentence'], 'sentence'])
            elif len(attr['entity']['node_text']) > 0:
                if attr['entity']['node_text'] in entity:
                    answers.append([attr['sentence'], 'sentence'])
            if len(attr['property_value']['node_text']) > 0 and attr['property_value']['node_text'] in entity:
                answers.append([attr['sentence'], 'property_value'])
    if len(answers) == 0:
        for entity_node in product_descriptions_attrs:
            if len(entity_node['entity']['node_text']) > 0 and entity_node['entity']['node_text'] in entity:
                for attr in entity_node['tuples']:
                    answers.append([attr['sentence'], 'entity'])
    if len(answers) == 0:
        for user_constraints_attr in user_constraints_attrs:
            for attr in user_constraints_attr['tuples']:
                if len(attr['attribute']['node_text']) > 0:
                    if attr['attribute']['node_text'] in entity:
                        answers.append([attr['sentence'], 'sentence'])
                elif len(attr['entity']['node_text']) > 0:
                    if attr['entity']['node_text'] in entity:
                        answers.append([attr['sentence'], 'sentence'])
                if len(attr['property_value']['node_text']) > 0 and attr['property_value']['node_text'] in entity:
                    answers.append([attr['sentence'], 'property_value'])
    if len(answers) == 0:
        for user_constraints_attr in user_constraints_attrs:
            if len(user_constraints_attr['entity']['node_text']) > 0 and user_constraints_attr['entity']['node_text'] in entity:
                for attr in user_constraints_attr['tuples']:
                    answers.append([attr['sentence'], 'entity'])
    return answers[:top_k]


def find_tuple_of_specific_entity_all_arguments(reason_graph_document, question_entity, reason_paths,
                                                match_score_threshold, similarity_tool, top_k=2):
    product_descriptions_attrs = reason_graph_document['product_descriptions_attrs']
    user_constraints_attrs = reason_graph_document['user_constraints_attrs']
    answers = []
    candidate_attrs = []
    scores = {
        'product_descriptions_attrs': [],
        'user_constraints_attrs': []
    }
    if len(question_entity) == 0:
        sys.exit('question_entity is empty!')
    for entity_node in product_descriptions_attrs:
        top_entity = entity_node['entity']['node_text']
        tuples = entity_node['tuples']
        entity_match_score = similarity_tool.compute_similarity(top_entity, question_entity)
        scores['product_descriptions_attrs'].append((entity_match_score, tuples))
        for attr in tuples:
            sub_entity = attr['entity']['node_text']
            attribute = attr['attribute']['node_text']
            sub_entity_property = attr['property_value']['node_text']
            if len(attribute) > 0:
                sub_entity = attribute
            if len(sub_entity_property) > 0:
                sub_entity = str(sub_entity + sub_entity_property)
            sub_entity_match_score = similarity_tool.compute_similarity(sub_entity, question_entity)
            scores['product_descriptions_attrs'].append((sub_entity_match_score, [attr]))
    for user_constraints_attr in user_constraints_attrs:
        top_entity = user_constraints_attr['entity']['node_text']
        tuples = user_constraints_attr['tuples']
        entity_match_score = similarity_tool.compute_similarity(top_entity, question_entity)
        scores['user_constraints_attrs'].append((entity_match_score, tuples))
        for attr in tuples:
            sub_entity = attr['entity']['node_text']
            attribute = attr['attribute']['node_text']
            sub_entity_property = attr['property_value']['node_text']
            if len(attribute) > 0:
                sub_entity = attribute
            if len(sub_entity_property) > 0:
                sub_entity = str(sub_entity + sub_entity_property)
            sub_entity_match_score = similarity_tool.compute_similarity(sub_entity, question_entity)
            scores['user_constraints_attrs'].append((sub_entity_match_score, [attr]))

    product_descriptions_scores = sorted(scores['product_descriptions_attrs'], key=lambda x: x[0], reverse=True)
    user_constraints_scores = sorted(scores['user_constraints_attrs'], key=lambda x: x[0], reverse=True)

    match_score = -1
    if len(product_descriptions_scores) > 0 and len(user_constraints_scores) > 0:
        product_top1 = product_descriptions_scores[0]
        user_top1 = user_constraints_scores[0]
        if product_top1[0] < user_top1[0]:
            candidate_attrs += [(user_top1[0], attr) for attr in user_top1[1]]
            candidate_attrs += [(product_top1[0], attr) for attr in product_top1[1]]
            match_score = user_top1[0]
        else:
            candidate_attrs += [(product_top1[0], attr) for attr in product_top1[1]]
            match_score = product_top1[0]
    else:
        all_scores = product_descriptions_scores + user_constraints_scores
        if len(all_scores) > 0:
            top1 = all_scores[0]
            candidate_attrs += [(top1[0], attr) for attr in top1[1]]
            match_score = top1[0]

    if match_score == -1 or match_score < match_score_threshold:
        return [], match_score

    for attr_tuple in candidate_attrs:
        attr = attr_tuple[1]
        answers.append(attr['sentence'])
        reason_paths.append(
            '[{}] attr_entity_match:{}->{}:{}'.format(attr_tuple[0], question_entity, attr['entity']['node_text'],
                                                      attr['sentence']))
    return answers[:top_k], match_score


def find_action_and_position(reason_graph_document, core_predicate, entities, object_entities):
    action_item = None
    row = -1
    col = -1
    links = reason_graph_document['links']
    for link_index, link in enumerate(links):
        for action_index, action in enumerate(link):
            matched = False
            if len(object_entities) == 0:
                if action['predicate'] == core_predicate:
                    matched = True
            else:
                if action['predicate'] == core_predicate and entities_match_argument(object_entities,
                                                                                     action['object']['node_text']):
                    matched = True
            if matched:
                action_item = action
                row = link_index
                col = action_index
                break

    return action_item, row, col


def answer_action_next_action(links, row, col, question_core_action, reason_paths):
    answers = []

    target_link = links[row]
    if col == len(target_link) - 1:
        return answers
    next_action = target_link[col + 1]
    sentence = next_action['sentence']
    predicate = next_action['predicate']
    reason_paths.append('next_action:{}->next->{}->{}'.format(question_core_action, predicate, sentence))
    answers.append(sentence)

    return answers


def answer_action_previous_action(links, row, col, question_core_action, reason_paths):
    answers = []

    target_link = links[row]
    if col == 0:
        return answers
    previous_action = target_link[col - 1]
    sentence = previous_action['sentence']
    predicate = previous_action['predicate']
    reason_paths.append('previous_action:{}->previous->{}->{}'.format(question_core_action, predicate, sentence))
    answers.append(sentence)

    return answers


def answer_for_declarative(extraction_item, entity_taxonomy, action_taxonomy, reason_graph_document,
                           match_score_threshold, similarity_tool, reason_paths, info_dict, debug, top_k=2):
    answers = []
    question_core_entity = entity_taxonomy['entity']
    attributes = entity_taxonomy['attribute']
    entity_property = entity_taxonomy['property']

    if debug:
        print('question_core_entity:', question_core_entity)
        print('attributes:', attributes)
        print('entity_property:', entity_property)

    question_entity = question_core_entity
    if len(attributes) > 0:
        question_entity = str(attributes + question_entity)
    if len(entity_property) > 0:
        question_entity = str(question_entity + entity_property)
    if len(question_entity) == 0:
        return answers, 0

    entity_answers, match_score = find_tuple_of_specific_entity_all_arguments(reason_graph_document, question_entity,
                                                                              reason_paths, match_score_threshold,
                                                                              similarity_tool, top_k=top_k)
    answers += entity_answers
    return answers[:top_k], match_score


def find_check_list_for_single_action(links, action_taxonomy, question_core_entities, reason_paths,
                                      match_score_threshold, similarity_tool):
    scores_all_actions = []
    if len(links) == 0:
        return -1, -1, -1
    question_action = action_taxonomy['action']
    question_object = action_taxonomy['object']['text']
    if question_object == '' or question_action == '':
        return -1, -1, -1
    for link_index, link in enumerate(links):
        for action_index, action in enumerate(link):
            action_predicate = action['predicate']
            action_object = action['object']['node_text']
            if action_object == '' or action_predicate == '':
                continue
            predicate_match_score = similarity_tool.compute_similarity(action_predicate, question_action)
            object_match_score = similarity_tool.compute_similarity(action_object, question_object)
            match_score = (predicate_match_score + object_match_score) / 2
            scores_all_actions.append((link_index, action_index, match_score))
    if len(scores_all_actions) == 0:
        return -1, -1, -1

    scores_all_actions = sorted(scores_all_actions, key=lambda x: x[2], reverse=True)
    target_action_info = scores_all_actions[0]
    target_row, target_col, target_score = target_action_info
    if target_score == 0 or target_score < match_score_threshold:
        return -1, -1, target_score

    return target_row, target_col, target_score


def find_linked_attrs(entity_linking, linked_id, find_top_entity=False, find_tuples=False):
    linked_attrs = []
    product_id_and_attrs = entity_linking['product_id_and_attrs']
    product_id_and_tuples = entity_linking['product_id_and_tuples']
    if linked_id in product_id_and_attrs:
        linked_attr = product_id_and_attrs[linked_id]
        linked_attrs.append(linked_attr)
    if len(linked_attrs) == 0 and find_top_entity:
        if linked_id in product_id_and_tuples:
            linked_tuple = product_id_and_tuples[linked_id]
            if len(linked_tuple) == 1:
                linked_attrs.append(linked_tuple[0])
            elif len(linked_tuple) > 1:
                if find_tuples:
                    linked_attrs += linked_tuple
                else:
                    linked_attrs.append(linked_tuple[0])
    return linked_attrs


def action_align_question(target_action, action_taxonomy, reason_paths, target_score, info_dict, previous_tag=False,
                          last_action=None):
    answers = []
    need_find_previous_action = False
    need_find_linked_info = False

    for arg in ['time', 'location', 'manner']:
        if len(action_taxonomy[arg]['text']) > 0:
            if len(target_action[arg]['node_text']) > 0:
                answers.append(target_action['sentence'])
                if previous_tag:
                    reason_paths.append(
                        '[{}] previous_action_arg:{}->{}->{}_{}->{}'.format(target_score, action_taxonomy['action'],
                                                                            last_action['predicate'],
                                                                            target_action['predicate'], arg,
                                                                            target_action[arg]['node_text']))
                else:
                    reason_paths.append(
                        '[{}] answer_in_arg:{}->{}_{}->{}'.format(target_score, action_taxonomy['action'],
                                                                  target_action['predicate'], arg,
                                                                  target_action[arg]['node_text']))
            else:
                need_find_previous_action = True

    negation = action_taxonomy['negation']
    reason = action_taxonomy['reason']['text']
    if len(negation) > 0 or len(reason) > 0:
        need_find_linked_info = True

    return answers, need_find_previous_action, need_find_linked_info


def find_answers_from_linked_info(question_core_action, links, action_row, action_col, entity_linking, reason_paths,
                                  target_score):
    answers = []
    linked_attrs = []
    linked_attrs_answers = []
    linked_arguments = []
    if action_row >= 0 and action_col >= 0:
        target_action = links[action_row][action_col]
        for argument_name in ['object', 'time', 'location',
                              'manner']:
            action_links = target_action[argument_name]['links']
            if len(action_links) > 0:
                linked_id = action_links[0]
                linked_attrs_this_id = find_linked_attrs(entity_linking, linked_id, find_top_entity=False,
                                                         find_tuples=False)
                if len(linked_attrs_this_id) > 0:
                    linked_attrs.append(linked_attrs_this_id[0])
                    linked_arguments.append(target_action[argument_name]['node_text'])
        for index, attr_item in enumerate(linked_attrs):
            linked_attrs_answers.append(attr_item['sentence'])
            reason_paths.append('[{}] linked_attr:{}->{}->{}->{}'.format(target_score, question_core_action,
                                                                         linked_arguments[index],
                                                                         attr_item['entity']['node_text'],
                                                                         attr_item['sentence']))
        answers += linked_attrs_answers
    state_linked_attrs = []
    state_linked_attrs_answers = []

    if action_row >= 0 and action_col >= 0:
        target_action = links[action_row][action_col]
        predicate = target_action['predicate']
        state_links = target_action['action_links']
        if len(state_links) > 0:
            linked_id = state_links[0]
            state_linked_attrs_this_id = find_linked_attrs(entity_linking, linked_id, find_top_entity=False,
                                                           find_tuples=False)
            if len(state_linked_attrs_this_id) > 0:
                state_linked_attrs.append(state_linked_attrs_this_id[0])
        for index, attr_item in enumerate(state_linked_attrs):
            state_linked_attrs_answers.append(attr_item['sentence'])
            reason_paths.append(
                '[{}] state_linking_attr:{}->{}->{}->{}'.format(target_score, question_core_action, predicate,
                                                                attr_item['entity']['node_text'],
                                                                attr_item['sentence']))
        answers += state_linked_attrs_answers
    return answers


def find_check_list_for_single_question_parsing(question_text, source_sentences, extraction_item, entity_taxonomy,
                                                action_taxonomy,
                                                reason_graph_document, reason_paths, similarity_tool, info_dict,
                                                match_score_threshold, top_k=5):
    links = reason_graph_document['links']
    entity_linking = {
        'user_id_and_tuples': reason_graph_document['user_id_and_tuples'],
        'product_id_and_tuples': reason_graph_document['product_id_and_tuples'],
        'user_id_and_attrs': reason_graph_document['user_id_and_attr'],
        'product_id_and_attrs': reason_graph_document['product_id_and_attr'],
    }
    question_core_action = action_taxonomy['action']
    question_core_entities = []
    for argument in ['subject', 'object']:
        if len(action_taxonomy[argument]['text']) > 0:
            if len(action_taxonomy[argument]['entity']) > 0:
                question_core_entities.append(action_taxonomy[argument]['entity'])

    check_list = []
    find_arg_answer = False
    action_row, action_col, target_score = \
        find_check_list_for_single_action(links, action_taxonomy, question_core_entities, reason_paths,
                                          match_score_threshold, similarity_tool)
    if action_row >= 0 and action_col >= 0:
        target_action = links[action_row][action_col]
        answers_for_target_action, need_find_previous_action, need_find_linked_info = \
            action_align_question(target_action, action_taxonomy, reason_paths, target_score, info_dict)
        if len(answers_for_target_action) > 0:
            check_list += answers_for_target_action
            find_arg_answer = True
            info_dict['factoid_style'] = True
            info_dict['q_type'] = 'factoid'
        else:
            if need_find_previous_action:
                info_dict['procedure_style'] = True
                info_dict['q_type'] = 'procedure'
            if need_find_linked_info:
                info_dict['inconsistent'] = True
                info_dict['q_type'] = 'inconsistency'
        if need_find_previous_action:
            if action_col > 0:
                previous_action = links[action_row][action_col - 1]
                answers_for_previous_action, _, _ = \
                    action_align_question(previous_action, action_taxonomy, reason_paths, target_score, info_dict,
                                          previous_tag=True, last_action=target_action)
                if len(answers_for_previous_action) > 0:
                    check_list += answers_for_previous_action
                    find_arg_answer = True
        if len(check_list) == 0:
            check_list.append(target_action['sentence'])
            reason_paths.append('[{}] action_only_sentence:{}->{}'.format(target_score, question_core_action,
                                                                          target_action['sentence']))
            if action_col > 0:
                check_list.append(links[action_row][action_col - 1]['sentence'])
                reason_paths.append(
                    '[{}] action_only_previous_sentence:{}->{}'.format(target_score, question_core_action,
                                                                       links[action_row][action_col - 1]['sentence']))
        else:
            pass
        if need_find_linked_info or not find_arg_answer:
            answers_from_linked_info = find_answers_from_linked_info(question_core_action, links, action_row,
                                                                     action_col, entity_linking, reason_paths,
                                                                     target_score)
            check_list += answers_from_linked_info
    else:
        pass
    user_constraints_answers = find_user_role_restriction(reason_graph_document, reason_paths, top_k=1)
    check_list += user_constraints_answers

    return check_list[:top_k], target_score
