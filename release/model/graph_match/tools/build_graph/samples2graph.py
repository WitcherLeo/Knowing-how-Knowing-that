from action_links.links_merging import merging_action_links
from attrs.build_taxonomy import construct_entities_taxonomy
from attrs.add_node_ids import add_node_ids_for_links_and_attrs


def read_sp_entities(sp_entities_file):
    with open(sp_entities_file, 'r', encoding='utf-8') as f:
        entities = f.read().split('\n')
    return entities


def get_id_and_corresponding_entity(attrs_with_taxonomy):
    id_and_entity = []
    for attrs_item in attrs_with_taxonomy:
        node_id = attrs_item['entity']['node_id']
        entity_list = attrs_item['entity']['entity_list']
        if len(entity_list) > 0:
            id_and_entity.append({'id': node_id, 'entity': entity_list})

        for attr_item in attrs_item['tuples']:
            for argument_name in ['attribute', 'property_value', 'patients', 'time', 'location', 'manner', 'cause']:
                item_node_id = attr_item[argument_name]['node_id']
                item_entity_list = attr_item[argument_name]['entity_list']
                if len(item_entity_list) > 0:
                    id_and_entity.append({'id': item_node_id, 'entity': item_entity_list})

    return id_and_entity


def item_match(entity, entity_list):
    for item in entity_list:
        if item in entity or entity in item:
            return True
    return False


def try_linking_entity(entities, id_and_entity):
    linked_ids = []
    for entity in entities:
        for id_entity in id_and_entity:
            node_id = id_entity['id']
            entity_list = id_entity['entity']
            if item_match(entity, entity_list):
                if node_id not in linked_ids:
                    linked_ids.append(node_id)
                    print('entity_link:', entity, '->', entity_list)
    return linked_ids


def get_ids_and_attr_arguments(attrs_with_taxonomy):
    ids_and_attr_arguments = []
    for attrs_item in attrs_with_taxonomy:
        for attr_item in attrs_item['tuples']:
            item_node_id = attr_item['action_id']
            item_argument = attr_item['action']
            if len(item_argument) > 0:
                ids_and_attr_arguments.append({'id': item_node_id, 'node_text': item_argument})

            for argument_name in ['attribute', 'property_value', 'patients', 'time', 'location', 'manner', 'cause']:
                item_node_id = attr_item[argument_name]['node_id']
                item_argument = attr_item[argument_name]['node_text']
                if len(item_argument) > 0:
                    ids_and_attr_arguments.append({'id': item_node_id, 'node_text': item_argument})
    return ids_and_attr_arguments


def try_linking_states(entities, ids_and_attr_arguments):
    linked_ids = []
    for entity in entities:
        for id_attr_argument in ids_and_attr_arguments:
            node_id = id_attr_argument['id']
            node_text = id_attr_argument['node_text']
            if entity in node_text:
                if node_id not in linked_ids:
                    linked_ids.append(node_id)
                    print('state_link:', entity, '->', node_text)
    return linked_ids


def entity_linking(links, user_constraints_attrs_with_taxonomy, product_descriptions_attrs_with_taxonomy):
    id_and_entity = []

    id_and_entity += get_id_and_corresponding_entity(user_constraints_attrs_with_taxonomy)
    id_and_entity += get_id_and_corresponding_entity(product_descriptions_attrs_with_taxonomy)

    ids_and_attr_arguments = []
    ids_and_attr_arguments += get_ids_and_attr_arguments(user_constraints_attrs_with_taxonomy)
    ids_and_attr_arguments += get_ids_and_attr_arguments(product_descriptions_attrs_with_taxonomy)

    for link_index, link in enumerate(links):
        for action_index, action_item in enumerate(link):
            predicate = action_item['predicate']
            state_linked_ids = try_linking_states([predicate], ids_and_attr_arguments)
            if len(state_linked_ids) > 0:
                links[link_index][action_index]['action_links'] = state_linked_ids
            for argument_name in ['object', 'time', 'location', 'manner']:
                entity_list = action_item[argument_name]['entity_list']
                linked_ids = try_linking_entity(entity_list, id_and_entity)
                if len(linked_ids) > 0:
                    links[link_index][action_index][argument_name]['links'] = linked_ids
    return links


def construct_graph(samples_with_boundary_labels_per_document, sp_entities, ltp_tool):
    graph_data_all_documents = []

    for document_data in samples_with_boundary_labels_per_document:
        document_id = document_data['document_id']
        question = document_data['question']
        graph_prediction = document_data['graph_prediction']
        links = graph_prediction['links']
        attrs = graph_prediction['attrs']

        links = merging_action_links(links)

        user_constraints_attrs, product_descriptions_attrs = \
            construct_entities_taxonomy(attrs, sp_entities, ltp_tool)
        links, user_constraints_attrs, product_descriptions_attrs = \
            add_node_ids_for_links_and_attrs(links, user_constraints_attrs, product_descriptions_attrs, sp_entities, ltp_tool)

        links = entity_linking(links, user_constraints_attrs, product_descriptions_attrs)

        graph_data_all_documents.append({
            'document_id': document_id,
            'question': question,
            'graph_prediction': {
                'links': links,
                'user_constraints_attrs': user_constraints_attrs,
                'product_descriptions_attrs': product_descriptions_attrs
            },
            'source_sentences': document_data['source_sentences']
        })

    return graph_data_all_documents
