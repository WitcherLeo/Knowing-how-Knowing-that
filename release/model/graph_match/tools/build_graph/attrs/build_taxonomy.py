import sys
from typing import List
from special_rules import using_rules


def contain_sp_model_words(text, list_of_sp_model_words):
    for sp_model_word in list_of_sp_model_words:
        if sp_model_word in text:
            return True
    return False


def entity_separation(input_text, ltp_tool, entities_human_labeled):
    core_entity = input_text
    modifier_part = ''

    input_text_is_user, core, modifier = contain_special_entity(input_text, entities_human_labeled)
    if input_text_is_user:
        core_entity = core
        modifier_part = modifier
        return core_entity, modifier_part, True

    dep_entity, dep_modifier, core_entity_postag = ltp_tool.entity_separation_dep(input_text)
    sdp_entity, sdp_modifier, _ = ltp_tool.entity_separation_sdp(input_text, mode='tree')
    separation_succeed = False
    if len(dep_entity) > 0:
        core_entity = dep_entity
        modifier_part = dep_modifier
        separation_succeed = True
    elif len(sdp_entity) > 0:
        core_entity = sdp_entity
        modifier_part = sdp_modifier
        separation_succeed = True
    else:
        print('核心实体分离失败:', input_text, 'postag:', core_entity_postag)

    return core_entity, modifier_part, separation_succeed


def contain_special_entity(text, entities_human_labeled):
    for item in entities_human_labeled:
        if item in text:
            index_of_item = text.index(item)
            if index_of_item + len(item) == len(text):
                modifier = text[:index_of_item]
                return True, item, modifier

    for item in entities_human_labeled:
        if item in text:
            index_of_item = text.index(item)
            if index_of_item == 0:
                modifier = text[index_of_item + len(item):]
                return True, item, modifier

    for item in entities_human_labeled:
        if item in text:
            index_of_item = text.index(item)
            modifier = text[index_of_item + len(item):]
            return True, item, modifier
    return False, '', ''


def merge_multi_tuples(multi_tuples_attrs):
    merged_multi_tuples_attrs = []
    for multi_tuple_attr in multi_tuples_attrs:
        if len(merged_multi_tuples_attrs) == 0:
            merged_multi_tuples_attrs.append([multi_tuple_attr])
            continue
        insert_flag = False
        for index, merged_multi_tuple_attr in enumerate(merged_multi_tuples_attrs):
            if multi_tuple_attr['entity']['node_text'] == merged_multi_tuple_attr[0]['entity']['node_text']:
                merged_multi_tuples_attrs[index].append(multi_tuple_attr)
                insert_flag = True
                break
        if not insert_flag:
            merged_multi_tuples_attrs.append([multi_tuple_attr])

    merged_multi_tuples_attrs_with_level = []
    for merged_multi_tuple_attr in merged_multi_tuples_attrs:
        new_tuple_attr = {
            'entity': {
                'node_text': merged_multi_tuple_attr[0]['entity']['node_text'],
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'tuples': merged_multi_tuple_attr,
        }
        merged_multi_tuples_attrs_with_level.append(new_tuple_attr)
    return merged_multi_tuples_attrs_with_level


def is_user(text, list_of_user_mentions):
    user = False
    for user_mention in list_of_user_mentions:
        if user_mention in text:
            user = True
            break
    return user


def classify_multi_tuples_attrs(multi_tuples_attrs):
    user_constraints = []
    product_descriptions = []

    list_of_user_mentions = ['用户']
    for multi_tuple_attr_list in multi_tuples_attrs:
        entity = multi_tuple_attr_list['entity']['node_text']
        is_user_constraint = False
        for user_mention in list_of_user_mentions:
            if user_mention in entity:
                user_constraints.append(multi_tuple_attr_list)
                is_user_constraint = True
                break
        if not is_user_constraint:
            product_descriptions.append(multi_tuple_attr_list)

    return user_constraints, product_descriptions


def contain_sp_predicate(predicate, list_of_sp_predicates):
    for sp_predicate in list_of_sp_predicates:
        if sp_predicate in predicate:
            return True
    return False


def rule_process_is_predicates(multi_tuples_attrs):
    list_of_sp_predicates = ['为', '是', '即']
    processed_attrs = []
    for attr in multi_tuples_attrs:
        if attr['modifier_texts'] == '':
            processed_attrs.append(attr)
            continue
        old_tails = []
        new_tails = []
        for index, tail in enumerate(attr['multi_tuples']['tails']):
            if tail['argument_type'] == 'object':
                if contain_sp_predicate(tail['relation'], list_of_sp_predicates):
                    attr['multi_tuples']['tails'][index]['relation'] = attr['modifier_texts']
                    processed_tail = {
                                        'argument_type': tail['argument_type'],
                                        'relation': attr['modifier_texts'],
                                        'node_text': tail['node_text'],
                                    }
                    new_tails.append(processed_tail)
                else:
                    old_tails.append(tail)
            else:
                old_tails.append(tail)
        if len(old_tails) > 0:
            attr['multi_tuples']['tails'] = old_tails
            processed_attrs.append(attr)
        if len(new_tails) > 0:
            processed_attr = {
                'subject': attr['head_noun'],
                'head_noun': attr['head_noun'],
                'modifier_texts': '',
                'multi_tuples': {
                    'head': attr['head_noun'],
                    'tails': new_tails,
                },
            }
            processed_attrs.append(processed_attr)
    return processed_attrs


def rule_process_possess_predicates(multi_tuples_attrs):
    list_of_sp_predicates_affirm = ['有']
    list_of_sp_predicates_negation = ['没有', '无']

    processed_attrs = []
    for attr in multi_tuples_attrs:
        for index, tail in enumerate(attr['multi_tuples']['tails']):
            if tail['argument_type'] == 'object':
                relation_this_tail = tail['relation']
                if contain_sp_predicate(relation_this_tail, list_of_sp_predicates_affirm) or \
                        contain_sp_predicate(relation_this_tail, list_of_sp_predicates_negation):
                    attr['multi_tuples']['tails'][index]['relation'] = \
                        attr['multi_tuples']['tails'][index]['node_text']
                    if contain_sp_predicate(relation_this_tail, list_of_sp_predicates_negation):
                        attr['multi_tuples']['tails'][index]['node_text'] = '无'
                    else:
                        attr['multi_tuples']['tails'][index]['node_text'] = '有'
        processed_attrs.append(attr)
    return processed_attrs


def try_merging(multi_tuple_attr, input_links):
    merged = False
    for index, final_link in enumerate(input_links):
        if len(final_link) > 0:
            first_attr = final_link[0]
            if multi_tuple_attr['head_noun'] == first_attr['head_noun']:
                input_links[index].append(multi_tuple_attr)
                merged = True
                break
    if not merged:
        input_links.append([multi_tuple_attr])
    return input_links


def build_entity_node(entity, links):
    entity_node = {
        'node_type': 'entity',
        'node_text': entity,
        'node_info': None,
        'links': links,
    }
    return entity_node


def build_tuples_node(tuples_attr, subject_text):
    tuples_node = {
        'node_type': 'tuples',
        'node_text': subject_text,
        'node_info': tuples_attr,
        'links': [],
    }
    return tuples_node


def build_taxonomy(multi_tuples_attrs):
    classified_links = []
    for multi_tuple_attr in multi_tuples_attrs:
        if len(classified_links) == 0:
            classified_links.append([multi_tuple_attr])
        else:
            classified_links = try_merging(multi_tuple_attr, classified_links)
    final_links = []
    for link in classified_links:
        if len(link) == 1:
            this_attr = link[0]
            subject_text = this_attr['subject']
            tuples_node = build_tuples_node(this_attr, subject_text)
            final_links.append(tuples_node)
        elif len(link) > 1:
            entity_node = build_entity_node(link[0]['subject'], [])
            for multi_tuple_attr in link:
                if len(multi_tuple_attr['modifier_texts']) == 0:
                    entity_node['node_info'] = multi_tuple_attr
                else:
                    entity_node['links'].append(multi_tuple_attr)
            final_links.append(entity_node)

    return final_links


def add_node_id_and_entity_recognition(attrs_with_taxonomy, node_id, ltp_tool):
    processed_attrs = []
    for node_taxonomy in attrs_with_taxonomy:
        node_text = node_taxonomy['node_text']
        processed_node = {
            'node_type': node_taxonomy['node_type'],
            'node_text': node_text,
            'node_id': node_id,
            'node_info': None,
        }
        node_id += 1
        dep_entity, dep_modifier, core_entity_postag = ltp_tool.entity_separation_dep(node_text)
        sdp_entity, sdp_modifier, _ = ltp_tool.entity_separation_sdp(node_text, mode='tree')
        core_entity = ''
        separation_succeed = False
        if len(dep_entity) > 0:
            core_entity = dep_entity
            separation_succeed = True
        elif len(sdp_entity) > 0:
            core_entity = sdp_entity
            separation_succeed = True
        else:
            pass
        if separation_succeed:
            processed_node['entities'] = [core_entity]
        else:
            processed_node['entities'] = []

        if node_taxonomy['node_info'] is not None:
            new_node_info = {
                'head': node_text,
                'tails': [],
            }
            for tail_node in node_taxonomy['node_info']['multi_tuples']['tails']:
                new_tail_node = {
                    'argument_type': tail_node['argument_type'],
                    'relation': tail_node['relation'],
                    'node_text': tail_node['node_text'],
                    'node_id': node_id,
                }
                node_id += 1
                dep_entity, dep_modifier, core_entity_postag = ltp_tool.entity_separation_dep(tail_node['node_text'])
                sdp_entity, sdp_modifier, _ = ltp_tool.entity_separation_sdp(tail_node['node_text'], mode='tree')
                core_entity = ''
                separation_succeed = False
                if len(dep_entity) > 0:
                    core_entity = dep_entity
                    separation_succeed = True
                elif len(sdp_entity) > 0:
                    core_entity = sdp_entity
                    separation_succeed = True
                else:
                    pass
                if separation_succeed:
                    new_tail_node['entities'] = [core_entity]
                else:
                    new_tail_node['entities'] = []
                new_node_info['tails'].append(new_tail_node)
            processed_node['node_info'] = new_node_info

        if len(node_taxonomy['links']) > 0:
            new_links = []
            for tuple_node in node_taxonomy['links']:
                new_tuple_node = {
                    'node_text': tuple_node['subject'],
                    'node_id': node_id,
                    'node_info': {
                        'head': tuple_node['subject'],
                        'tails': [],
                    },
                }
                node_id += 1
                dep_entity, dep_modifier, core_entity_postag = ltp_tool.entity_separation_dep(tuple_node['subject'])
                sdp_entity, sdp_modifier, _ = ltp_tool.entity_separation_sdp(tuple_node['subject'], mode='tree')
                core_entity = ''
                separation_succeed = False
                if len(dep_entity) > 0:
                    core_entity = dep_entity
                    separation_succeed = True
                elif len(sdp_entity) > 0:
                    core_entity = sdp_entity
                    separation_succeed = True
                else:
                    pass
                if separation_succeed:
                    new_tuple_node['entities'] = [core_entity]
                else:
                    new_tuple_node['entities'] = []

                new_tails = []
                for tail_node in tuple_node['multi_tuples']['tails']:
                    new_tail_node = {
                        'argument_type': tail_node['argument_type'],
                        'relation': tail_node['relation'],
                        'node_text': tail_node['node_text'],
                        'node_id': node_id,
                    }
                    node_id += 1
                    dep_entity, dep_modifier, core_entity_postag = ltp_tool.entity_separation_dep(tail_node['node_text'])
                    sdp_entity, sdp_modifier, _ = ltp_tool.entity_separation_sdp(tail_node['node_text'], mode='tree')
                    core_entity = ''
                    separation_succeed = False
                    if len(dep_entity) > 0:
                        core_entity = dep_entity
                        separation_succeed = True
                    elif len(sdp_entity) > 0:
                        core_entity = sdp_entity
                        separation_succeed = True
                    else:
                        pass
                    if separation_succeed:
                        new_tail_node['entities'] = [core_entity]
                    else:
                        new_tail_node['entities'] = []
                    new_tails.append(new_tail_node)
                new_tuple_node['node_info']['tails'] = new_tails
                new_links.append(new_tuple_node)
            processed_node['links'] = new_links
        else:
            processed_node['links'] = []

        processed_attrs.append(processed_node)

    return processed_attrs, node_id


def subject_separation(subject, object_text, predicate, sp_entities):
    entity = subject
    attribute = ''
    entity_property = ''

    sub_obj_reverse = False
    user_indicators = ['用户']
    for user_indicator in user_indicators:
        if user_indicator in object_text:
            sub_obj_reverse = True
            break

    if sub_obj_reverse:
        subject, object_text = object_text, subject

    find_sp_entity = False
    for sp_entity in sp_entities:
        if sp_entity in subject:
            find_sp_entity = True
            entity = sp_entity
            entity_start_index = subject.index(entity)
            if entity_start_index > 0:
                attribute = subject[:entity_start_index]
            if len(subject) > entity_start_index + len(entity):
                entity_property = subject[entity_start_index + len(entity):]
            break

    if not find_sp_entity:
        for sp_entity in sp_entities:
            if sp_entity in object_text:
                find_sp_entity = True
                if not sub_obj_reverse:
                    subject, object_text = object_text, subject
                else:
                    print('error: 主语和宾语已经翻转，但是主语中没有找到特殊实体！')
                    sys.exit(1)
                entity = sp_entity
                entity_start_index = subject.index(entity)
                if entity_start_index > 0:
                    attribute = subject[:entity_start_index]
                if len(subject) > entity_start_index + len(entity):
                    entity_property = subject[entity_start_index + len(entity):]
                break
    if not find_sp_entity:
        pass

    return entity, attribute, entity_property, object_text, sub_obj_reverse


def add_items2string(new_states: List, action_state_str: str):
    action_state_str = action_state_str.strip()
    action_states = action_state_str.split('|')
    action_states += new_states
    new_action_state_str = '|'.join(action_states)
    return new_action_state_str


def construct_entities_taxonomy(attrs, sp_entities, ltp_tool):
    entities_human_labeled = ['用户']
    entities_human_labeled += sp_entities
    entities_human_labeled = list(set(entities_human_labeled))
    entities_human_labeled.sort(key=lambda x: len(x), reverse=True)

    multi_tuples_attrs = []
    for attr in attrs:
        sentence = attr['sentence']
        extraction_label = attr['label']
        subject = extraction_label['subject']
        object_text = extraction_label['object']
        predicate = extraction_label['predicate']
        negation = extraction_label['negation']
        relation = extraction_label['relation']
        attachment = extraction_label['attachment']
        action_states = []
        for state in [negation, relation, attachment]:
            if len(state) > 0:
                action_states.append(state)
        action_state = '|'.join(action_states)
        if subject == '':
            if object_text != '':
                subject = object_text
                object_text = ''
                action_state = add_items2string(['被'], action_state)
            else:
                print('warning: 没有主语也没有宾语。谓词：', predicate)
                continue
        entity, attribute, entity_property, object_text, sub_obj_reverse = \
            subject_separation(subject, object_text, predicate, sp_entities)
        attribute = attribute + entity if len(attribute) > 0 else ''

        if sub_obj_reverse:
            action_state = add_items2string(['被'], action_state)
        new_attr = {
            'sentence': sentence,
            'action': predicate,
            'action_id': -1,
            'action_state': {
                'node_text': action_state,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'entity': {
                'node_text': entity,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'attribute': {
                'node_text': attribute,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'property': {
                'node_text': entity_property,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'property_value': {
                'node_text': '',
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'patients': {
                'node_text': object_text,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'time': {
                'node_text': extraction_label['time'],
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'location': {
                'node_text': extraction_label['location'],
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'manner': {
                'node_text': extraction_label['manner'],
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
            'cause': {
                'node_text': extraction_label['reason'],
                'node_id': -1,
                'entity_list': [],
                'links': [],
            },
        }

        sp_predicates_is = ['是', '为', '即']
        for sp_predicate in sp_predicates_is:
            if predicate == sp_predicate:
                new_attr['property_value']['node_text'] = new_attr['patients']['node_text']
                new_attr['patients'] = {
                    'node_text': '',
                    'node_id': -1,
                    'entity_list': [],
                    'links': [],
                }
                break

        new_attr = using_rules(new_attr)
        multi_tuples_attrs.append(new_attr)

    multi_tuples_attrs = merge_multi_tuples(multi_tuples_attrs)

    user_constraints_attrs, product_descriptions_attrs = classify_multi_tuples_attrs(multi_tuples_attrs)

    return user_constraints_attrs, product_descriptions_attrs
