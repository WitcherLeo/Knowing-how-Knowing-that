

def get_id_and_corresponding_entity(attrs_with_taxonomy):
    id_and_tuples = {}
    id_and_attr = {}
    for attrs_item in attrs_with_taxonomy:
        node_id = attrs_item['entity']['node_id']
        tuples = attrs_item['tuples']
        if len(tuples) > 0:
            id_and_tuples[node_id] = tuples
        for attr_item in attrs_item['tuples']:
            for argument_name in ['attribute', 'property_value', 'patients', 'time', 'location', 'manner', 'cause']:
                item_node_id = attr_item[argument_name]['node_id']
                id_and_attr[item_node_id] = attr_item

    return id_and_tuples, id_and_attr


def build_graph_data_for_reasoning(all_documents_info, is_label=False):
    reason_graph_all_documents = {}
    for document_index, document_info in enumerate(all_documents_info):
        document_id = document_info['document_id']
        document_id = int(document_id)
        reason_graph = {
            'document_id': document_id,
        }

        if is_label:
            graph_data = {
                'links': document_info['links'],
                'user_constraints_attrs': document_info['user_constraints_attrs'],
                'product_descriptions_attrs': document_info['product_descriptions_attrs'],
            }
        else:
            graph_data = document_info['graph_prediction']

        links = graph_data['links']
        user_constraints_attrs = graph_data['user_constraints_attrs']
        product_descriptions_attrs = graph_data['product_descriptions_attrs']

        user_id_and_tuples, user_id_and_attr = get_id_and_corresponding_entity(user_constraints_attrs)
        product_id_and_tuples, product_id_and_attr = get_id_and_corresponding_entity(product_descriptions_attrs)

        reason_graph['links'] = links
        reason_graph['user_constraints_attrs'] = user_constraints_attrs
        reason_graph['product_descriptions_attrs'] = product_descriptions_attrs

        reason_graph['user_id_and_tuples'] = user_id_and_tuples
        reason_graph['product_id_and_tuples'] = product_id_and_tuples
        reason_graph['user_id_and_attr'] = user_id_and_attr
        reason_graph['product_id_and_attr'] = product_id_and_attr
        reason_graph['source_sentences'] = document_info['source_sentences']

        reason_graph_all_documents[int(document_id)] = reason_graph

    return reason_graph_all_documents

