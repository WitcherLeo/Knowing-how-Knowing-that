

def ner_ltp(node_text, ltp_tool):
    if len(node_text) == 0:
        return []
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
        return [core_entity]
    else:
        return []


def get_entities_for_links(text, sp_entities, ltp_tool):
    entities = []
    for entity in sp_entities:
        if entity in text:
            entities.append(entity)
    if len(entities) == 0:
        entities = ner_ltp(text, ltp_tool)
    return entities


def get_entities_for_attrs(text, sp_entities, ltp_tool):
    entities = []
    for entity in sp_entities:
        if entity in text:
            entities.append(entity)
            break
    if len(entities) == 0:
        entities = ner_ltp(text, ltp_tool)
    return entities


def add_node_ids_for_links_and_attrs(links, user_attrs, product_attrs, sp_entities, ltp_tool):
    node_id = 0
    for link_index, link in enumerate(links):
        for action_index, action_item in enumerate(link):
            for argument_name in ['object', 'time', 'location', 'manner']:
                argument = action_item[argument_name]['node_text']
                links[link_index][action_index][argument_name]['node_id'] = node_id
                node_id += 1
                if len(argument) == 0:
                    continue
                links[link_index][action_index][argument_name]['entity_list'] = \
                    get_entities_for_links(argument, sp_entities, ltp_tool)
            action_item['node_id'] = node_id
            node_id += 1

    for user_attr_index, user_attr_list_item in enumerate(user_attrs):
        user_attrs[user_attr_index]['entity']['node_id'] = node_id
        node_id += 1
        if len(user_attr_list_item['entity']['node_text']) > 0:
            user_attrs[user_attr_index]['entity']['entity_list'] = \
                get_entities_for_attrs(user_attr_list_item['entity']['node_text'], sp_entities, ltp_tool)
        user_attr_list = user_attr_list_item['tuples']
        for item_index, user_attr_item in enumerate(user_attr_list):
            user_attrs[user_attr_index]['tuples'][item_index]['action_id'] = node_id
            node_id += 1

            for argument_name in ['entity', 'attribute', 'property', 'property_value', 'patients',
                                  'time', 'location', 'manner', 'cause']:
                argument = user_attr_item[argument_name]['node_text']
                user_attrs[user_attr_index]['tuples'][item_index][argument_name]['node_id'] = node_id
                node_id += 1
                if len(argument) == 0:
                    continue
                user_attrs[user_attr_index]['tuples'][item_index][argument_name]['entity_list'] = \
                    get_entities_for_attrs(argument, sp_entities, ltp_tool)

    for product_attr_index, product_attr_list_item in enumerate(product_attrs):
        product_attrs[product_attr_index]['entity']['node_id'] = node_id
        node_id += 1
        if len(product_attr_list_item['entity']['node_text']) > 0:
            product_attrs[product_attr_index]['entity']['entity_list'] = \
                get_entities_for_attrs(product_attr_list_item['entity']['node_text'], sp_entities, ltp_tool)
        product_attr_list = product_attr_list_item['tuples']
        for item_index, product_attr_item in enumerate(product_attr_list):
            product_attrs[product_attr_index]['tuples'][item_index]['action_id'] = node_id
            node_id += 1
            for argument_name in ['entity', 'attribute', 'property', 'property_value', 'patients',
                                  'time', 'location', 'manner', 'cause']:
                argument = product_attr_item[argument_name]['node_text']
                product_attrs[product_attr_index]['tuples'][item_index][argument_name]['node_id'] = node_id
                node_id += 1
                if len(argument) == 0:
                    continue
                product_attrs[product_attr_index]['tuples'][item_index][argument_name]['entity_list'] = \
                    get_entities_for_attrs(argument, sp_entities, ltp_tool)
    return links, user_attrs, product_attrs

