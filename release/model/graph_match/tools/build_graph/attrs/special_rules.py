

def rule1_role_limitation(attr):
    sp_predicates = ['视为']

    predicate = attr['action']
    for sp_predicate in sp_predicates:
        if sp_predicate == predicate:
            attr['property']['node_text'] = '角色限制'
            attr['property_value']['node_text'] = attr['patients']['node_text']
            attr['action'] = ''
            attr['action_state'] = {
                'node_text': '',
                'node_id': -1,
                'entity_list': [],
                'links': [],
            }
            attr['patients']['node_text'] = ''
            break
    return attr


def using_rules(attr):
    rule_funcs = [rule1_role_limitation]
    for rule_func in rule_funcs:
        attr = rule_func(attr)

    return attr

