

def entity_find_ltp(argument, ltp_tool):
    find_core_entity = False
    entity = ''
    attribute = ''

    core_entity, modifier_part, core_entity_postag = ltp_tool.entity_separation_dep(argument)
    if len(core_entity) > 0:
        entity = core_entity
        attribute = modifier_part
        find_core_entity = True
    else:
        core_entity, modifier_part, core_entity_postag = ltp_tool.entity_separation_sdp(argument)
        if len(core_entity) > 0:
            entity = core_entity
            attribute = modifier_part
            find_core_entity = True
    return find_core_entity, entity, attribute


def argument_separation(argument, sp_entities):
    entity = argument
    attribute = ''
    entity_property = ''

    find_sp_entity = False
    for sp_entity in sp_entities:
        if sp_entity in argument:
            find_sp_entity = True
            entity = sp_entity
            entity_start_index = argument.index(entity)
            if entity_start_index > 0:
                attribute = argument[:entity_start_index]
            if len(argument) > entity_start_index + len(entity):
                entity_property = argument[entity_start_index + len(entity):]
            break
    return find_sp_entity, entity, attribute, entity_property


def construct_action_taxonomy(extracted_item, sp_entities):
    subject = extracted_item['subject']
    object_text = extracted_item['object']
    time = extracted_item['time']
    location = extracted_item['location']
    manner = extracted_item['manner']
    reason = extracted_item['reason']

    action_taxonomy = {
        'sentence': extracted_item['sentence'],
        'action': extracted_item['predicate'],
        'negation': extracted_item['negation'],
        'relation': extracted_item['relation'],
        'attachment': extracted_item['attachment'],
        'subject': {
            'text': subject,
            'entity': '',
        },
        'object': {
            'text': object_text,
            'entity': '',
        },
        'time': {
            'text': time,
            'entity': '',
        },
        'location': {
            'text': location,
            'entity': '',
        },
        'manner': {
            'text': manner,
            'entity': '',
        },
        'reason': {
            'text': reason,
            'entity': '',
        },
    }
    for argument in ['subject', 'object', 'time', 'location', 'manner', 'reason']:
        if len(action_taxonomy[argument]['text']) > 0:
            find_sp_entity, entity, attribute, entity_property = argument_separation(action_taxonomy[argument]['text'], sp_entities)
            if find_sp_entity:
                action_taxonomy[argument]['entity'] = entity
                action_taxonomy[argument]['attribute'] = attribute
                action_taxonomy[argument]['property'] = entity_property
    return action_taxonomy


def construct_entity_taxonomy(extracted_item, sp_entities, ltp_tool):
    entities_human_labeled = ['用户']
    entities_human_labeled += sp_entities
    entities_human_labeled = list(set(entities_human_labeled))
    entities_human_labeled.sort(key=lambda x: len(x), reverse=True)

    sentence = extracted_item['sentence']
    subject = extracted_item['subject']
    object_text = extracted_item['object']
    predicate = extracted_item['predicate']
    negation = extracted_item['negation']
    relation = extracted_item['relation']
    attachment = extracted_item['attachment']

    entity = ''
    attribute = ''
    entity_property = ''
    find_core_entity = False
    if len(subject) > 0:
        find_sp_entity_sub, entity_sub, attribute_sub, entity_property_sub = \
            argument_separation(subject, sp_entities)
        if find_sp_entity_sub:
            entity = entity_sub
            attribute = attribute_sub
            entity_property = entity_property_sub
            find_core_entity = True
    if not find_core_entity:
        if len(object_text) > 0:
            find_sp_entity_obj, entity_obj, attribute_obj, entity_property_obj = \
                argument_separation(object_text, sp_entities)
            if find_sp_entity_obj:
                entity = entity_obj
                attribute = attribute_obj
                entity_property = entity_property_obj
                find_core_entity = True
    if not find_core_entity:
        if len(subject) > 0:
            find_entity_sub_ltp, entity_sub_ltp, attribute_sub_ltp = entity_find_ltp(subject, ltp_tool=ltp_tool)
            if find_entity_sub_ltp:
                entity = entity_sub_ltp
                attribute = attribute_sub_ltp
                find_core_entity = True
        if not find_core_entity:
            if len(object_text) > 0:
                find_entity_obj_ltp, entity_obj_ltp, attribute_obj_ltp = entity_find_ltp(object_text, ltp_tool=ltp_tool)
                if find_entity_obj_ltp:
                    entity = entity_obj_ltp
                    attribute = attribute_obj_ltp
                    find_core_entity = True

    if not find_core_entity:
        entity = object_text if len(object_text) > 0 else subject
        attribute = ''
        entity_property = ''

    entity_taxonomy = {
        'sentence': sentence,
        'action': predicate,
        'entity': entity,
        'attribute': attribute,
        'property': entity_property,
        'property_value': '',
        'patients': object_text,
        'negation': negation,
        'relation': relation,
        'attachment': attachment,
    }

    return entity_taxonomy
