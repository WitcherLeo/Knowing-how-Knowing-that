def try_to_insert_link2target_link(insert_link, target_link):
    find_insert_node = False
    insert_node_index_source = -1
    insert_node_index_target = -1
    for insert_index, insert_link_item in enumerate(insert_link):
        if not find_insert_node:
            for target_index, target_link_item in enumerate(target_link):
                insert_link_item_action = insert_link_item['predicate']
                target_link_item_action = target_link_item['predicate']
                if insert_link_item_action in target_link_item_action or target_link_item_action in insert_link_item_action:
                    find_insert_node = True
                    insert_node_index_source = insert_index
                    insert_node_index_target = target_index
                    break
        else:
            break

    if find_insert_node:
        insert_sentence = insert_link[insert_node_index_source]['sentence']
        constraints_all = [target_link[insert_node_index_target]['constraints']['node_text']] if \
            len(target_link[insert_node_index_target]['constraints']['node_text']) > 0 else []
        constraints_all.append(insert_sentence)
        target_link[insert_node_index_target]['constraints']['node_text'] = '|'.join(constraints_all)

        merged_link = target_link[:insert_node_index_target] + insert_link[:insert_node_index_source] + \
                      [target_link[insert_node_index_target]]

        if insert_node_index_source != len(insert_link) - 1:
            merged_link += insert_link[insert_node_index_source + 1:]
        if insert_node_index_target != len(target_link) - 1:
            merged_link += target_link[insert_node_index_target + 1:]

        return True, merged_link
    else:
        return False, None


def merging_action_links(links):
    new_links_multi_arguments = []
    for link in links:
        new_link = []
        for item in link:
            new_item = {
                'sentence': item['sentence'],
                'predicate': item['label']['predicate'],
                'subject': {'node_text': item['label']['subject'],
                            'node_id': -1,
                            'entity_list': [],
                            'links': []},
                'object': {'node_text': item['label']['object'],
                           'node_id': -1,
                           'entity_list': [],
                           'links': []},
                'time': {'node_text': item['label']['time'],
                         'node_id': -1,
                         'entity_list': [],
                         'links': []},
                'location': {'node_text': item['label']['location'],
                             'node_id': -1,
                             'entity_list': [],
                             'links': []},
                'manner': {'node_text': item['label']['manner'],
                           'node_id': -1,
                           'entity_list': [],
                           'links': []},
                'constraints': {'node_text': '',
                                'node_id': -1,
                                'entity_list': [],
                                'links': []},
                'action_links': [],
                'node_id': -1,
            }
            negation = item['label']['negation']
            relation = item['label']['relation']
            attachment = item['label']['attachment']
            action_states = []
            for state in [negation, relation, attachment]:
                if len(state) > 0:
                    action_states.append(state)
            action_state = '|'.join(action_states)
            new_item['action_state'] = {
                'node_text': action_state,
                'node_id': -1,
                'entity_list': [],
                'links': [],
            }
            new_link.append(new_item)
        new_links_multi_arguments.append(new_link)
    links = new_links_multi_arguments

    if len(links) == 0:
        return []

    return links
