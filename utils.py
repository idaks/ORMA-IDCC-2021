from itertools import product
import re
import pandas as pd


def add_filter(operator):
    facets = operator['engineConfig']
    if facets:
        selection = 0
        pass
    else:
        pass


def find_neighbors(nodes_list):
    # @in: [[(a,b), (a,c)], [(b,d)],...]
    # @return: step_id, derived affected columns
    neighbors_of = {}
    nodes = set()
    for process in nodes_list:
        for edge in process:
            u = edge[0]
            v = edge[1]
            nodes.add(u)
            nodes.add(v)
            neighbors_of.setdefault(u, []).append(v)
            neighbors_of.setdefault(v, []).append(u)
    return neighbors_of, nodes


def find_component(neighbors_of, u, component=None):
    if component is None:
        component = {u}
    for v in neighbors_of[u]:
        if v in component:
            continue
        component.add(v)
        find_component(neighbors_of, v, component)
    return component

def check_occurrance(list_depends, val):
    flags = []
    for dep in list_depends:
        flag = []
        for pairs in dep:
            if val in pairs:
                flag.append(True)
                break
            else:
                flag.append(False)
        flags.append(any(flag))
    return flags


def depend_on_step(dict_cols_neigh, depend_ser:pd.Series):
    # Input dictionary of neighbors for column names, return corresponding step ids
    # @params dict_cols_neigh: {'State': ['State', 'State', 'Place'],...'...': ['Season1Date_from']}
    # @params depend_ser: dependency column from pandas table  
    # @return dict_ops_neigh: {3: [3,5]...} dependency information on operation/step level 
    dict_ops_nei = {}
    list_depends = list(depend_ser)
    for k,v in dict_cols_neigh.items():
        v_neigh = []
        occurrances = check_occurrance(list_depends, k) # return [False, True,...]
        for val in v:
            val_occur = check_occurrance(list_depends, val)
            val_T_occur = [id for id,x in enumerate(val_occur) if x is True]
            val_steps_occur = [depend_ser.index[x] for x in val_T_occur] 
            v_neigh.extend(val_steps_occur)
        T_occur = [id for id,x in enumerate(occurrances) if x is True]
        steps_occur = [depend_ser.index[x] for x in T_occur]
        k_id = steps_occur[0]         # the first occurrance step id as the key
        dict_ops_nei[k_id] = list(set(v_neigh))
    return dict_ops_nei


def extract_col(operator):
    # This function is to return column node from the transformation
    # => determine the potential affected transformations and column nodes
    if 'op' not in operator:
        print('This is not a operation')
        pass
    else:
        if operator['op'] == 'core/column-addition':  # merge operation
            exp = operator['expression']
            if exp.split(':')[0] == 'grel':
                if re.findall(r'cells.(\w+).value', exp):
                    col = re.findall(r'cells.(\w+).value', exp)
                elif re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp):
                    col = re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp)
                else:
                    col = operator['baseColumnName']
            else:
                col = operator['baseColumnName'] 

        elif operator['op'] == 'core/column-split':  # split operation
            col = operator["columnName"] 
        elif operator['op'] == 'core/column-rename':  # split operation
            col = operator["oldColumnName"]
        elif operator['op'] == 'core/column-removal':
            col = operator["columnName"]
        elif operator['op'] == 'core/column-addition-by-fetching-urls':
            col = operator['baseColumnName']
        # elif operator['op'] == 'core/multivalued-cell-join':
        #     col = operator["columName"]
        elif operator['op'] == 'core/transpose-columns-into-rows':
            col = operator["startColumnName"]
        # elif operator['op'] == 'core/row-removal':
        #     colname = operator["engineConfig"]["facets"][0]["columnName"]
        # elif operator['op'] == 'core/column-move':
        #     col = operator["columnName"]
        elif operator['op'] == 'core/mass-edit':
            col = operator["columnName"]
        # elif operator['op'] == 'core/multivalued-cell-split':
        #     col = operator["columnName"]
        elif operator['op'] == 'core/recon':
            col = operator['columnName']
        else:  # normal unary operation
            try:
                col = operator['columnName']
            except KeyError:
                pass
        return col 

def unit_test(repair_df):
    repair_df['dependency'] = repair_df.apply(lambda row: list(product(row['from_schema'], row['to_schema'])),
                                             axis=1)
    print(repair_df['dependency'])
    neighbors_of, nodes = find_neighbors(list(repair_df['dependency']))


def dfs(graph, u):
    visited_nodes = [u]
    try:
        for v in graph[u]:
            visited_nodes += dfs(graph, v)
    except KeyError:
        pass
    return visited_nodes


def graph_op_model(nodes_list, dep_ser:pd.Series):
    # @params nodes_list: [op1, op2,...opn]
    # @params dep_ser: dependency series
    # @return: {
    # op1: [op1_dep, op1_dep',...]
    # op2: [op2_dep, op2_dep',...]
    # ...
    # }
    graph = {}
    # print(nodes_list) # 【3，4，5，6，7，8，9】
    for i,op in enumerate(nodes_list):
        row = dep_ser.loc[[op]].iloc[0]
        to_nodes = list(set([val[1] for val in row]))
        for op_cur in nodes_list[i+1:]:
            row_cur = dep_ser.loc[[op_cur]].iloc[0]
            from_nodes = list(set([val[0] for val in row_cur]))
            # print(f'{op} >>> {op_cur}')
            if list(set(from_nodes) & set(to_nodes)):
                graph.setdefault(op, []).append(op_cur)
                # graph.setdefault(op_cur, []).append(op)
    return graph
    

def main():
    mydict = { 3: [('State', 'State')], 
               4: [('city', 'City')], 
               5: [('State', 'Place'), ('City', 'Place')], 
               6: [('Season1Date', 'Season1Date 1'), ('Season1Date', 'Season1Date 2'), ('Season1Date', 'Season1Date 3')],
               7: [('Season1Date 1', 'Season1Date_from')],
               8: [('State', 'State')],
               9: [('Season1Date_from', 'Season1Date_from')]
               }
    ser = pd.Series(data=mydict, index=[3,4,5,6,7,8,9])
    print(ser)
    col_neighbors = {'State': ['State', 'State', 'Place', 'State'], 
           'city': ['City'], 'City': ['city', 'Place'], 
           'Place': ['State', 'City'], 
           'Season1Date': ['Season1Date 1', 'Season1Date 2', 'Season1Date 3'], 
           'Season1Date 1': ['Season1Date', 'Season1Date_from'],
           'Season1Date_from': ['Season1Date 1', 'Season1Date_from']}
    # res = depend_on_step(col_neighbors, ser)
    # print(res)
    steps_list = list(ser.index)
   
    graph_steps = graph_op_model(steps_list, ser)
    print(graph_steps)
    
    for step in steps_list:
        graph_steps[step] = dfs(graph_steps, step)
    print(graph_steps)
    # print(res)



if __name__ == '__main__':
    main()



    # {'State': ['State', 'State', 'Place'], 
    # 'city': ['City'], 
    # 'City': ['city', 'Place'], 
    # 'Place': ['State', 'City'], 
    # 'Season1Date': ['Season1Date 1', 'Season1Date 2', 'Season1Date 3'], 
    # 'Season1Date 1': ['Season1Date', 'Season1Date_from'], 
    # 'Season1Date 2': ['Season1Date', 'Season1Date_to'], 
    # 'Season1Date 3': ['Season1Date'], 
    # 'Season1Date_from': ['Season1Date 1', 'valid_Season1Date_from_flag', 'Season1Date_from', 'Season1Date_from'],
    #  'Season1Date_to': ['Season1Date 2'], 'valid_Season1Date_from_flag': ['Season1Date_from']}