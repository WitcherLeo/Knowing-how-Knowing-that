from queue import Queue


def find_directly_connected_nodes(graph_data, index_of_target_node):
    list_to_return = []
    for index, item in enumerate(graph_data):
        if item[1] > -2 and item[1] == index_of_target_node:
            list_to_return.append(item[6])
    list_to_return = list(set(list_to_return))
    return list_to_return


def find_all_connected_nodes_bfs(graph_data, index_of_target_node):
    list_of_all_connected_nodes_bfs = [index_of_target_node]

    queue_of_find_nodes = Queue()

    indexes_directly_connected = find_directly_connected_nodes(
        graph_data, index_of_target_node)
    for index in indexes_directly_connected:
        queue_of_find_nodes.put(index)

    # BFS
    while not queue_of_find_nodes.empty():
        head_index = queue_of_find_nodes.get()
        indexes_directly_connected_for_head = find_directly_connected_nodes(
            graph_data, head_index)
        for index in indexes_directly_connected_for_head:
            if index not in list_of_all_connected_nodes_bfs:
                queue_of_find_nodes.put(index)
        list_of_all_connected_nodes_bfs.append(head_index)
    return list_of_all_connected_nodes_bfs


def take_2th_item(elem):
    return elem[1]


def add_info_to_dic(dic_for_analyse, info):
    if info in dic_for_analyse:
        dic_for_analyse[info] += 1
    else:
        dic_for_analyse[info] = 1


def get_text_for_single_node(graph_data,
                             index_of_target_node, dic_for_statistics, words):
    list_of_connected_nodes = find_all_connected_nodes_bfs(
        graph_data, index_of_target_node)
    list_of_connected_nodes.sort()
    start_index_new = list_of_connected_nodes[0]
    end_index_new = list_of_connected_nodes[-1]

    text_after_fusion = ''
    for index in list_of_connected_nodes:
        text_after_fusion += words[index]

    return text_after_fusion, start_index_new, end_index_new


def find_argument_text_for_single_label(
        graph_data, index_of_key_token, label, dic_for_statistics, words):

    list_of_all_sub_graph_data = []
    list_of_neighbor_nodes = find_neighbor_nodes(
        graph_data, index_of_key_token, label)
    for index_of_node in list_of_neighbor_nodes:
        text_after_fusion, start_index, end_index = \
            get_text_for_single_node(graph_data, index_of_node,
                                     dic_for_statistics, words)
        list_of_all_sub_graph_data.append(
            (text_after_fusion, start_index, end_index))

    text_for_this_label = ''
    start_index_new = -1
    end_index_new = -1
    if len(list_of_all_sub_graph_data) > 0:
        list_of_all_sub_graph_data.sort(key=take_2th_item)
        start_index_new = list_of_all_sub_graph_data[0][1]
        end_index_new = list_of_all_sub_graph_data[-1][2]
        for index, sub_graph_data in enumerate(list_of_all_sub_graph_data):
            if index == 0:
                text_for_this_label += sub_graph_data[0]
            else:
                if sub_graph_data[1] == \
                        list_of_all_sub_graph_data[index - 1][2] + 1:
                    text_for_this_label += sub_graph_data[0]
                else:
                    text_for_this_label += '|' + sub_graph_data[0]

    return text_for_this_label, start_index_new, end_index_new


def get_indexes_of_adv_and_cmp(graph_data, index_of_key_token):
    list_of_indexes_for_adv_cmp = []
    list_of_find_node_indexes_adv = find_neighbor_nodes(
        graph_data, index_of_key_token, 'ADV')
    list_of_find_node_indexes_cmp = find_neighbor_nodes(
        graph_data, index_of_key_token, 'CMP')
    list_of_find_node_indexes = \
        list_of_find_node_indexes_adv + list_of_find_node_indexes_cmp
    for find_node_index in list_of_find_node_indexes:
        indexes_of_sub_tree = \
            find_all_connected_nodes_bfs(graph_data, find_node_index)
        list_of_indexes_for_adv_cmp.append(indexes_of_sub_tree)
    return list_of_indexes_for_adv_cmp


def check_contain_labels(
        graph_data, index_of_key_token,
        role_labels, dic_for_statistics, words):
    check_list = []
    for index, label in enumerate(role_labels):
        text_for_this_label, start_index_new, end_index_new = \
            find_argument_text_for_single_label(graph_data,
                                                index_of_key_token,
                                                label,
                                                dic_for_statistics,
                                                words)
        if len(text_for_this_label) > 0 and \
                start_index_new != -1 and end_index_new != -1:
            check_list.append(
                (True, text_for_this_label, start_index_new, end_index_new))
        else:
            check_list.append(
                (False, text_for_this_label, start_index_new, end_index_new))

    return check_list


def deal_with_patient_roles_sdgp(
        graph_data, index_of_key_token, words, dic_for_statistics):
    patient_role_labels = \
        ['PAT', 'CONT', 'DATV', 'LINK', 'dPAT', 'dCONT', 'dDATV', 'dLINK']
    check_list = check_contain_labels(
        graph_data, index_of_key_token,
        patient_role_labels, dic_for_statistics, words)

    if check_list[1][0] and check_list[2][0]:
        return True, (check_list[2][1], check_list[2][2], check_list[2][3]), (
            check_list[1][1], check_list[1][2], check_list[1][3])
    if check_list[0][0] and check_list[2][0]:
        return True, (check_list[2][1], check_list[2][2], check_list[2][3]), (
            check_list[0][1], check_list[0][2], check_list[0][3])

    list_of_all_text_tuples = []
    for item in check_list:
        if item[0]:
            list_of_all_text_tuples.append((item[1], item[2], item[3]))

    list_of_all_text_tuples.sort(key=take_2th_item)
    new_start_index = -1
    new_end_index = -1
    text_for_this_argument = ''
    if len(list_of_all_text_tuples) > 0:
        new_start_index = list_of_all_text_tuples[0][1]
        new_end_index = list_of_all_text_tuples[-1][2]
        for index, agent_role_text_info in enumerate(list_of_all_text_tuples):
            if index == 0:
                text_for_this_argument += agent_role_text_info[0]
            else:
                if agent_role_text_info[1] == \
                        list_of_all_text_tuples[index - 1][2] + 1:
                    text_for_this_argument += agent_role_text_info[0]
                else:
                    text_for_this_argument += '|' + agent_role_text_info[0]

    return False, ('', -1, -1), (
        text_for_this_argument, new_start_index, new_end_index)


def deal_with_patient_roles_dep(
        graph_data, index_of_key_token, words, dic_for_statistics):
    predicate_init = words[index_of_key_token]
    predicate = predicate_init
    text_for_vob, start_index_vob, end_index_vob = \
        find_argument_text_for_single_label(graph_data, index_of_key_token,
                                            'VOB', dic_for_statistics, words)
    text_for_fob, start_index_fob, end_index_fob = \
        find_argument_text_for_single_label(graph_data,
                                            index_of_key_token, 'FOB',
                                            dic_for_statistics, words)
    if end_index_vob <= start_index_fob:
        text_for_direct_object = str(text_for_vob + text_for_fob)
    elif end_index_fob <= start_index_vob:
        text_for_direct_object = str(text_for_fob + text_for_vob)
    else:
        text_for_direct_object = str(text_for_vob + text_for_fob)
    text_for_patient = text_for_direct_object

    text_for_iob, start_index_iob, end_index_iob = \
        find_argument_text_for_single_label(graph_data,
                                            index_of_key_token, 'IOB',
                                            dic_for_statistics, words)
    text_for_dbl, start_index_dbl, end_index_dbl = \
        find_argument_text_for_single_label(graph_data,
                                            index_of_key_token, 'DBL',
                                            dic_for_statistics, words)
    if len(text_for_dbl) > 0 and \
            start_index_dbl != -1 and end_index_dbl != -1:
        text_for_patient = text_for_dbl
        predicate = str(predicate_init + text_for_direct_object)

    direct_object = text_for_patient
    indirect_object = ''
    if len(text_for_dbl) == 0:
        if len(text_for_iob) > 0 and \
                start_index_iob != -1 and end_index_iob != -1:
            indirect_object = text_for_iob

    return predicate, direct_object, indirect_object


def deal_with_agent_roles(graph_data, index_of_key_token, agent_role_labels,
                          words, dic_for_statistics,
                          dic_for_analyse, analyse=False):
    list_of_agent_role_text_info = []
    for agent_role_label in agent_role_labels:
        text_for_this_label, start_index_new, end_index_new = \
            find_argument_text_for_single_label(graph_data,
                                                index_of_key_token,
                                                agent_role_label,
                                                dic_for_statistics,
                                                words)
        if len(text_for_this_label) > 0 and \
                start_index_new != -1 and end_index_new != -1:
            list_of_agent_role_text_info.append(
                (text_for_this_label, start_index_new, end_index_new))
            if analyse:
                add_info_to_dic(dic_for_analyse, agent_role_label)
    list_of_agent_role_text_info.sort(key=take_2th_item)
    text_for_this_argument = ''
    for index, agent_role_text_info in \
            enumerate(list_of_agent_role_text_info):
        if index == 0:
            text_for_this_argument += agent_role_text_info[0]
        else:
            if agent_role_text_info[1] == \
                    list_of_agent_role_text_info[index - 1][2] + 1:
                text_for_this_argument += agent_role_text_info[0]
            else:
                text_for_this_argument += '|' + agent_role_text_info[0]

    return text_for_this_argument


def get_text_char_index(words, index):
    word = words[index]
    text_before_predicate = ''.join(words[:index])
    predicate_index_start = len(text_before_predicate)
    predicate_index_end = predicate_index_start + len(word)
    return predicate_index_start, predicate_index_end


def get_text_char_index_range(words, index_start, index_end):
    char_index_start, _ = get_text_char_index(words, index_start)
    _, char_index_end = get_text_char_index(words, index_end)
    return char_index_start, char_index_end


def deal_with_hed_node_dep(
        graph_data, index_of_key_token,
        dic_for_statistics, words, dic_for_analyse):
    agent_role_labels = ['SBV']
    text_for_argument_agent = deal_with_agent_roles(
        graph_data, index_of_key_token, agent_role_labels, words,
        dic_for_statistics, dic_for_analyse, analyse=False)

    predicate, direct_object, indirect_object = deal_with_patient_roles_dep(
        graph_data, index_of_key_token, words, dic_for_statistics)

    list_of_indexes_for_adv_cmp = get_indexes_of_adv_and_cmp(
        graph_data, index_of_key_token)

    arguments_dic = {
        'agent': text_for_argument_agent,
        'direct_object': direct_object,
        'indirect_object': indirect_object,
        'index_of_predicate': index_of_key_token,
        'predicate': predicate,
        'list_of_indexes_for_adv_cmp': list_of_indexes_for_adv_cmp,
    }
    return arguments_dic


def deal_with_situational_roles_for_analyse(graph_data, index_of_key_token,
                                            words, dic_for_statistics,
                                            dic_for_analyse):
    situational_role_labels = ['MANN', 'REAS', 'TIME', 'LOC', 'TOOL',
                               'MATL', 'SCO', 'MEAS', 'STAT', 'FEAT',
                               'dMANN', 'dREAS', 'dTIME', 'dLOC', 'dTOOL',
                               'dMATL', 'dSCO', 'dMEAS', 'dSTAT', 'dFEAT']
    for situational_role_label in situational_role_labels:
        text_for_this_label_agt, start_index_new, end_index_new = \
            find_argument_text_for_single_label(graph_data,
                                                index_of_key_token,
                                                situational_role_label,
                                                dic_for_statistics,
                                                words)
        if len(text_for_this_label_agt) > 0 and \
                start_index_new != -1 and end_index_new != -1:
            add_info_to_dic(dic_for_analyse, situational_role_label)


def get_argument_text_for_target_roles(
        graph_data, index_of_key_token,
        role_labels, words, dic_for_statistics):
    list_of_agent_role_text_info = []
    for agent_role_label in role_labels:
        text_for_this_label, start_index_new, end_index_new = \
            find_argument_text_for_single_label(graph_data,
                                                index_of_key_token,
                                                agent_role_label,
                                                dic_for_statistics,
                                                words)
        if len(text_for_this_label) > 0 and \
                start_index_new != -1 and end_index_new != -1:
            list_of_agent_role_text_info.append(
                (text_for_this_label, start_index_new, end_index_new))

    list_of_agent_role_text_info.sort(key=take_2th_item)
    text_for_this_argument = ''
    for index, agent_role_text_info in \
            enumerate(list_of_agent_role_text_info):
        if index == 0:
            text_for_this_argument += agent_role_text_info[0]
        else:
            if agent_role_text_info[1] == \
                    list_of_agent_role_text_info[index - 1][2] + 1:
                text_for_this_argument += agent_role_text_info[0]
            else:
                text_for_this_argument += '|' + agent_role_text_info[0]

    return text_for_this_argument


def get_argument_text_for_target_roles_with_index(
        graph_data, index_of_key_token,
        role_labels, words, dic_for_statistics):
    list_of_agent_role_text_info = []
    for agent_role_label in role_labels:
        text_for_this_label, start_index_new, end_index_new = \
            find_argument_text_for_single_label(graph_data,
                                                index_of_key_token,
                                                agent_role_label,
                                                dic_for_statistics,
                                                words)
        if len(text_for_this_label) > 0 and \
                start_index_new != -1 and end_index_new != -1:
            list_of_agent_role_text_info.append(
                (text_for_this_label, start_index_new, end_index_new))

    list_of_agent_role_text_info.sort(key=take_2th_item)
    text_for_this_argument = ''
    total_start_index = -1
    total_end_index = -1
    if len(list_of_agent_role_text_info) > 0:
        total_start_index = list_of_agent_role_text_info[0][1]
        total_end_index = list_of_agent_role_text_info[-1][2]
    for index, agent_role_text_info in \
            enumerate(list_of_agent_role_text_info):
        if index == 0:
            text_for_this_argument += agent_role_text_info[0]
        else:
            if agent_role_text_info[1] == \
                    list_of_agent_role_text_info[index - 1][2] + 1:
                text_for_this_argument += agent_role_text_info[0]
            else:
                text_for_this_argument += '|' + agent_role_text_info[0]

    return text_for_this_argument, total_start_index, total_end_index


def deal_with_hed_node_operation_predicate(
        graph_data, index_of_key_token,
        dic_for_statistics, words, dic_for_analyse):

    predicate = words[index_of_key_token]
    agent_role_labels = ['AGT', 'EXP', 'dAGT', 'dEXP']
    text_for_argument_agent = deal_with_agent_roles(
        graph_data, index_of_key_token, agent_role_labels, words,
        dic_for_statistics, dic_for_analyse, analyse=False)

    indirect_object, (text_for_indirect_object,
                      new_start_index_indirect_object,
                      new_end_index_indirect_object), (
        text_for_direct_object, new_start_index_direct_object,
        new_end_index_direct_object) = deal_with_patient_roles_sdgp(
        graph_data, index_of_key_token, words, dic_for_statistics)

    if indirect_object:
        text_for_argument_patient = text_for_indirect_object
        predicate = str(predicate + text_for_direct_object)
    else:
        text_for_argument_patient = str(text_for_direct_object)
    start_index_object = new_start_index_direct_object
    end_index_object = new_end_index_direct_object

    mann_role_labels = ['MANN', 'dMANN', 'TOOL',
                        'dTOOL', 'MATL', 'dMATL']
    text_for_mann = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, mann_role_labels,
        words, dic_for_statistics)

    reas_role_labels = ['REAS', 'dREAS']
    text_for_reas = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, reas_role_labels,
        words, dic_for_statistics)

    time_role_labels = ['TIME', 'dTIME']
    text_for_time = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, time_role_labels,
        words, dic_for_statistics)
    loc_role_labels = ['LOC', 'dLOC']
    text_for_loc = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, loc_role_labels,
        words, dic_for_statistics)

    agt_roles = ['AGT', 'dAGT']
    text_for_agt = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, agt_roles,
        words, dic_for_statistics)
    exp_roles = ['EXP', 'dEXP']
    text_for_exp = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, exp_roles,
        words, dic_for_statistics)

    negation_role_labels = ['mNEG']
    text_for_negation, negation_start_index, negation_end_index = \
        get_argument_text_for_target_roles_with_index(graph_data, index_of_key_token, negation_role_labels,
                                                      words, dic_for_statistics)

    relation_role_labels = ['mRELA']
    text_for_relation = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, relation_role_labels,
        words, dic_for_statistics)

    attachment_role_labels = ['mDEPD']
    text_for_attachment = get_argument_text_for_target_roles(
        graph_data, index_of_key_token, attachment_role_labels,
        words, dic_for_statistics)

    arguments_dic = {
        'agent': text_for_argument_agent,
        'patient': text_for_argument_patient,
        'mann': text_for_mann,
        'reas': text_for_reas,
        'time': text_for_time,
        'loc': text_for_loc,
        'predicate': predicate,
        'negation': text_for_negation,
        'relation': text_for_relation,
        'attachment': text_for_attachment,
        'text_for_agt': text_for_agt,
        'text_for_exp': text_for_exp,
    }

    arguments_dic['start_index_object'] = start_index_object
    arguments_dic['end_index_object'] = end_index_object
    arguments_dic['negation_start_index'] = negation_start_index
    arguments_dic['negation_end_index'] = negation_end_index

    return arguments_dic


def find_neighbor_nodes(graph_data, index_of_key_token, relation):
    list_of_find_node_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] > -2 and item[1] == \
                index_of_key_token and item[2] == relation:
            list_of_find_node_indexes.append(item[6])
    list_of_find_node_indexes = list(set(list_of_find_node_indexes))
    return list_of_find_node_indexes


def find_all_neighbor_nodes_exp_trigger_tag(graph_data, index_of_key_token):
    list_of_find_node_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] > -2 and item[1] == \
                index_of_key_token and item[2] not in ['eCOO', 'ePREC', 'eSUCC']:
            list_of_find_node_indexes.append(item[6])
    list_of_find_node_indexes = list(set(list_of_find_node_indexes))
    return list_of_find_node_indexes


def find_trigger_node_dep(
        graph_data, index_of_key_token, index_of_candidate_triggers):
    list_of_labels_connect_triggers = ['COO', 'IS']
    for label in list_of_labels_connect_triggers:
        list_of_indexes_of_neighbor_nodes = find_neighbor_nodes(
            graph_data, index_of_key_token, label)
        for index_of_neighbor_node in list_of_indexes_of_neighbor_nodes:
            if index_of_neighbor_node not in index_of_candidate_triggers:
                index_of_candidate_triggers.append(index_of_neighbor_node)
                find_trigger_node_dep(
                    graph_data, index_of_neighbor_node,
                    index_of_candidate_triggers)


def find_trigger_node_sdgp(graph_data, index_of_key_token, candidate_triggers_exist):
    list_of_labels_connect_triggers = ['eCOO', 'ePREC', 'eSUCC']

    index_of_candidate_triggers = []
    direct_indexes_of_neighbor_nodes = []
    for label in list_of_labels_connect_triggers:
        list_of_indexes_of_neighbor_nodes = find_neighbor_nodes(
            graph_data, index_of_key_token, label)
        direct_indexes_of_neighbor_nodes.extend(list_of_indexes_of_neighbor_nodes)

    current_find_nodes = [index for index in candidate_triggers_exist]
    for index_of_neighbor_node in direct_indexes_of_neighbor_nodes:
        if index_of_neighbor_node not in current_find_nodes:
            index_of_candidate_triggers.append(index_of_neighbor_node)
            current_find_nodes.append(index_of_neighbor_node)
            find_triggers_this = find_trigger_node_sdgp(graph_data, index_of_neighbor_node,
                                                        current_find_nodes)
            index_of_candidate_triggers.extend(find_triggers_this)
            current_find_nodes.extend(find_triggers_this)

    return index_of_candidate_triggers


def find_key_nodes(graph_data):
    list_of_key_nodes_indexes = []
    for index, item in enumerate(graph_data):
        if item[1] == -1:
            list_of_key_nodes_indexes.append(item[6])
    list_of_key_nodes_indexes = list(set(list_of_key_nodes_indexes))
    return list_of_key_nodes_indexes


def node_fusion_for_single_graph_sdgp(
        graph, cat_path, title, label_for_title,
        dic_for_analyse, dic_for_statistics=None):
    if dic_for_statistics is None:
        dic_for_statistics = {}
    if 'sub_label' in graph:
        sub_label = graph['sub_label']
    else:
        sub_label = ''
    text = graph['text']
    words = graph['words']
    postags = graph['postags']
    sdgp_word_indexes = graph['sdgp_word_indexes']
    heads = graph['sdgp_heads']
    relations = graph['sdgp_relations']

    start_indexes = [index for index, word in enumerate(words)]
    end_indexes = [index for index, word in enumerate(words)]

    graph_data = []
    for sdgp_reword_num, word_index in enumerate(sdgp_word_indexes):
        info_this_reword = [words[word_index - 1], heads[sdgp_reword_num], relations[sdgp_reword_num], postags[word_index - 1],
                            start_indexes[word_index - 1], end_indexes[word_index - 1], word_index]
        graph_data.append(info_this_reword)

    for index, item in enumerate(graph_data):
        graph_data[index][1] -= 1
    for index, item in enumerate(graph_data):
        graph_data[index][6] -= 1

    punctuations_to_remove = ['，', '。', '；', '！', '？', '?', '!', ';']
    for index, item in enumerate(graph_data):
        if item[1] > -2 and item[2] == 'mPUNC' and \
                item[0] in punctuations_to_remove:
            graph_data[index][1] = -2
    indexes_of_key_tokens = find_key_nodes(graph_data)
    index_of_candidate_triggers = [index for index in indexes_of_key_tokens]
    predicates_link_root_node = [index for index in indexes_of_key_tokens]

    for index_of_key_token in predicates_link_root_node:
        index_of_candidate_triggers_this_turn = find_trigger_node_sdgp(
            graph_data, index_of_key_token, index_of_candidate_triggers)
        index_of_candidate_triggers.extend(index_of_candidate_triggers_this_turn)

    items_extracted = []
    index_of_candidate_triggers.sort()
    for index in index_of_candidate_triggers:
        state_description_dic = deal_with_hed_node_operation_predicate(
            graph_data, index, dic_for_statistics, words,
            dic_for_analyse)
        state_description_dic['index_of_predicate'] = index
        predicate_index_start, predicate_index_end = \
            get_text_char_index(words, index)
        state_description_dic['predicate_index_start'] = \
            predicate_index_start
        state_description_dic['predicate_index_end'] = \
            predicate_index_end
        if state_description_dic['start_index_object'] != -1:
            start_char_index_object, end_char_index_object = get_text_char_index_range(
                words, state_description_dic['start_index_object'], state_description_dic['end_index_object'])
        else:
            start_char_index_object, end_char_index_object = -1, -1
        state_description_dic['start_char_index_object'] = start_char_index_object
        state_description_dic['end_char_index_object'] = end_char_index_object
        if state_description_dic['negation_start_index'] != -1:
            start_char_index_negation, end_char_index_negation = get_text_char_index_range(
                words, state_description_dic['negation_start_index'], state_description_dic['negation_end_index'])
        else:
            start_char_index_negation, end_char_index_negation = -1, -1
        state_description_dic['start_char_index_negation'] = start_char_index_negation
        state_description_dic['end_char_index_negation'] = end_char_index_negation

        start_index_list = []
        for item_index in [start_char_index_negation, start_char_index_object, predicate_index_start]:
            if item_index != -1:
                start_index_list.append(item_index)
        state_description_dic['op_start_char_index'] = min(start_index_list) if len(start_index_list) > 0 else -1
        end_index_list = []
        for item_index in [end_char_index_negation, end_char_index_object, predicate_index_end]:
            if item_index != -1:
                end_index_list.append(item_index)
        state_description_dic['op_end_char_index'] = max(end_index_list) if len(end_index_list) > 0 else -1

        all_nodes_exp_trigger = [index]
        neighbor_nodes_indexes_exp_trigger = find_all_neighbor_nodes_exp_trigger_tag(graph_data, index)
        for index_of_neighbor_node in neighbor_nodes_indexes_exp_trigger:
            if index_of_neighbor_node not in all_nodes_exp_trigger:
                all_connected_nodes_bfs = find_all_connected_nodes_bfs(graph_data, index_of_neighbor_node)
                all_nodes_exp_trigger.extend(all_connected_nodes_bfs)

        all_nodes_exp_trigger = list(set(all_nodes_exp_trigger))
        all_nodes_exp_trigger.sort()
        sent_start_index = all_nodes_exp_trigger[0]
        sent_end_index = all_nodes_exp_trigger[-1]

        sent_char_start_index, sent_char_end_index = get_text_char_index_range(words, sent_start_index, sent_end_index)
        state_description_dic['sent_char_start_index'] = sent_char_start_index
        state_description_dic['sent_char_end_index'] = sent_char_end_index

        sub_sentence = text[sent_char_start_index:sent_char_end_index]
        state_description_dic['sub_sentence'] = sub_sentence

        state_description_dic['cat_path'] = cat_path
        state_description_dic['title'] = title
        state_description_dic['label_for_title'] = label_for_title
        state_description_dic['sub_label'] = sub_label
        state_description_dic['text'] = text
        items_extracted.append(state_description_dic)

    return items_extracted
