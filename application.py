from itertools import combinations

import pandas

in_mem_data = {}
in_mem_data_with_loose_rules = {'Global': set()}


def index_file(file_path):
    condition_to_key = {'>': "GT", '<': "LT", '=': "EQ"}
    df = pandas.read_csv(file_path, ",")
    for i in range(len(df)):
        group_id = df['Group'][i]
        rules = df['Rules'][i]
        rules = rules.split(";")
        rule_set = []
        for rule in rules:
            attribute, condition, value = parse_rule(rule)
            rule_set.append((attribute, condition, value))
        rule_set = sorted(rule_set, key=lambda x: x[0])
        level = in_mem_data
        len_rule_set = len(rule_set)
        for i in range(len_rule_set):
            attribute, condition, value = rule_set[i]
            if attribute not in level:
                level[attribute] = {'keys': set()}
            level = level[attribute]
            level['keys'].add(value)
            if value not in level:
                level[value] = {'*': {'LT': set(), 'GT': set(), 'EQ': set()}}
            if i == len_rule_set-1:
                level[value]['*'][condition_to_key[condition]].add(group_id)
            else:
                if condition_to_key[condition] not in level[value]:
                    level[value][condition_to_key[condition]] = {}
                level = level[value][condition_to_key[condition]]

            # Indexing for Rule Matching with missing data
            level1 = in_mem_data_with_loose_rules
            level1['Global'].add(group_id)
            if attribute not in level1:
                level1[attribute] = {'keys': set(), 'Global': set()}
            level1 = level1[attribute]
            level1['keys'].add(value)
            level1['Global'].add(group_id)
            if value not in level1:
                level1[value] = {'LT': set(), 'GT': set(), 'EQ': set()}
            level1[value][condition_to_key[condition]].add(group_id)


def parse_rule(rule):
    condition = ''
    rule = str.replace(rule, ")", "")
    rule = str.replace(rule, "(", "")
    if '=' in rule:
        rule = rule.split('=')
        condition = '='
    elif '>' in rule:
        rule = rule.split('>')
        condition = '>'
    elif '<' in rule:
        rule = rule.split('<')
        condition = '<'
    return rule[0], condition, rule[1]


def parse_entity_attribute(entity):
    entity = entity.split('=')
    return entity[0], entity[1]


def match_groups(entity, inequality_operator_inclusion):
    entity = str.replace(entity, ")", "")
    entity = str.replace(entity, "(", "")
    entity = entity.split(";")
    entity_attributes = []
    if "=" in entity[0]:
        for attribute in entity:
            entity_attributes.append((parse_entity_attribute(attribute)))
    entity_attributes = sorted(entity_attributes, key=lambda x:x[0])
    result_set = set()
    for L in range(0, len(entity_attributes) + 1):
        for subset in combinations(entity_attributes, L):
            level = in_mem_data
            result_set = result_set.union(match_attribute_values_rules(subset, level, inequality_operator_inclusion))
    return result_set


def match_attribute_values_rules(subset, level, inequality_operator_inclusion):
    len_rule_set = len(subset)
    if len_rule_set < 1:
        return set()
    final_level = False
    result_set = set()
    i = 0
    attribute, value = subset[i][0], subset[i][1]
    if attribute not in level:
        return set()
    level = level[attribute]
    if i == len_rule_set - 1:
        final_level = True
    if inequality_operator_inclusion:
        for key in level['keys']:
            level = level[key]
            if final_level:
                level = level['*']
            if value > key:
                if 'GT' in level:
                    if final_level:
                        result_set = result_set.union(level['GT'])
                    else:
                        result_set = result_set.union(match_attribute_values_rules(subset[i+1:], level['GT'], inequality_operator_inclusion))
            elif value < key:
                if 'LT' in level:
                    if final_level:
                        result_set = result_set.union(level['LT'])
                    else:
                        result_set = result_set.union(match_attribute_values_rules(subset[i+1:], level['LT'], inequality_operator_inclusion))
            else:
                if 'EQ' in level:
                    if final_level:
                        result_set = result_set.union(level['EQ'])
                    else:
                        result_set = result_set.union(match_attribute_values_rules(subset[i+1:], level['EQ'], inequality_operator_inclusion))
    else:
        if value in level:
            result_set = result_set.union(level['*']['EQ'])
    return result_set


def match_groups_with_loose_rules(entity, inequality_operator_inclusion):
    entity = str.replace(entity, ")", "")
    entity = str.replace(entity, "(", "")
    entity = entity.split(";")
    entity_attributes = []
    if "=" in entity[0]:
        for attribute in entity:
            entity_attributes.append((parse_entity_attribute(attribute)))
    result_set = in_mem_data_with_loose_rules['Global']
    for attribute, value in entity_attributes:
        temp_attribute_data = None
        if attribute in in_mem_data_with_loose_rules:
            temp_attribute_data = in_mem_data_with_loose_rules[attribute]
        if inequality_operator_inclusion:
            invalid_sets = temp_attribute_data['Global']
            for key in temp_attribute_data['keys']:
                if key > value:
                    invalid_sets = invalid_sets - temp_attribute_data[key]['LT']
                elif key < value:
                    invalid_sets = invalid_sets - temp_attribute_data[key]['GT']
                else:
                    invalid_sets = invalid_sets - temp_attribute_data[key]['EQ']
            result_set = result_set - invalid_sets
        else:
            if value in temp_attribute_data:
                result_set = result_set - (temp_attribute_data['Global'] -
                                           temp_attribute_data[value]['EQ'])
            else:
                result_set = result_set - temp_attribute_data['Global']
    return result_set


if __name__ == '__main__':
    inequality_rules_inclusion = input("You want to include rules with inequality(<,>)? Y/N:\n")
    if inequality_rules_inclusion == "Y" or "y":
        inequality_rules_inclusion = True
    else:
        inequality_rules_inclusion = False
    file_path_rules = input("Please provide the path to file with Entity Group Rules: \n")
    print("Indexing your data......")
    index_file(file_path_rules)
    print("Complete!\n")
    match_type = input("How do you want to feed query entities? (F)ile or (I)nput via Keyboard?\n")
    if match_type == "F":
        filepath = input("Please enter the path to file containing entities for search:\n")
        rule_match = input("How do you want to match? (B)lanket match for missing attributes or S(trict) match?\n")
        df = pandas.read_csv(filepath, ",")
        for i in range(len(df)):
            entity_id = df['Entity'][i]
            entity = df['Attributes'][i]
            if rule_match == "S":
                result = match_groups(entity, inequality_rules_inclusion)
            elif rule_match == "B":
                result = match_groups_with_loose_rules(entity, inequality_rules_inclusion)
            print(entity_id, "->", entity, "->", result)
    else:
        entity = None
        entity = input("Enter the entity in format: (attribute1=value1;attribute2=value2;....) or 'q' to quit:\n")
        while entity != "q":
            rule_match = input("How do you want to match? (B)lanket match for missing attributes or S(trict) match?\n")
            if rule_match == "S":
                result = match_groups(entity, inequality_rules_inclusion)
            elif rule_match == "B":
                result = match_groups_with_loose_rules(entity, inequality_rules_inclusion)
            print("Match Result:\n", entity, "=>", result)
            entity = input("Enter the entity in format: (attribute1=value1;attribute2=value2;....) or 'q' to quit:\n")



