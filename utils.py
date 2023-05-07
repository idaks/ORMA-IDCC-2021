from itertools import product
import re
import pandas as pd
import json 
from DTA.dataset import Dataset
from refine_pkg.OpenRefineClientPy3.google_refine.refine import refine


def oh_map_history(op):
    '''
        operation history from data.txt
        => include a complete record (single-edit; star/flag rows)
    '''
    oh_list = op.get_operations()

    '''
        history list: 
        history id; time stamp; description [retrospective provenance]
    '''
    histories = op.list_history()  # history id/ time/ desc
    past_histories = histories['past']

    assert len(oh_list) == len(past_histories)
    map_result = [
        {**oh, **history}
        for oh, history in zip(oh_list, past_histories)
    ]
    # description will be overwrite with retrospective info from history list.
    return oh_list, past_histories, map_result


def run_DTA(project_id, col_name):
    # run DTA on each status, return data model 
    # assumption: operation work on column level
    '''
    @params project_id: project id
    @params col_name: column name
    '''
    ds = Dataset(project_id=project_id)
    ds.read_ds()
    row_I, col_J = ds.get_index()
    contents, structure = ds.get_model()
    labels = ds.get_semantics(col_name=col_name)
    return (labels, contents, structure, row_I, col_J)
  
def exe_dm_delta(prev_dm, cur_dm):
    # Given two data model by DTA; compute the difference
    # Categorize the delta types: [value-level; schema-level]
    
    pass


def get_delta_type(step_ids, project_id=1689182305388, recipe='demo_recipes/depen_analysis_exp2.json'): 
    # This function to 
    # 1. execute the changes by the given operation
    # 2. run DTA to check how changes affect dataset 
    """
    @params step_ids: list of descendant columns 
    @params project_id: project id
    @params recipe: json file 
    """
    res = {}
    or_server = refine.RefineProject(refine.RefineServer(), project_id) # load openrefine project 
    or_server.undo_redo_project(0) # initialize project status 
    or_server.apply_operations(recipe)
    _, _, map_result = oh_map_history(or_server)
    for op_idx,op_dict in enumerate(1,map_result):
        col_name = extract_col(op_dict)
        if op_idx in step_ids:
            prev_idx = op_idx-1
            if prev_idx <0:
                assert prev_idx == -1
                # in this case, previous status is the clean dataset 
                prev_history_id = 0  
            else:
                prev_history_id = map_result[prev_idx]['id']
            cur_history_id = op_dict['id']
            or_server.undo_redo_project(prev_history_id)
            #TODO: DTA should run on old outputs (by old operator) and 
            # new outputs (after editing the old operator)
            prev_dm = run_DTA(project_id=project_id, col_name=col_name)
            or_server.undo_redo_project(cur_history_id)
            cur_dm = run_DTA(project_id=project_id, col_name=col_name)
            delta_type = exe_dm_delta(prev_dm, cur_dm)
            res[op_idx] = delta_type    
    return res


def depend_col(df):
    # @params json_data: recipe data in JSON format 
    # @params df: process data model in pandas dataframe 
    # @return: dictionary of dependency relationships at Column Level 
    row_count = df.shape[0]
    df['dependency'] = df.apply(lambda row: list(product(row['from_schema'], row['to_schema'])),
                                             axis=1)
    dep_col = df['dependency']
    col_list = list(dep_col)
    label_edges, label_nodes, neighbors = label_status_cols(col_list)
    from_node_label = add_col_labels(label_edges)
    to_node_label = add_col_labels(label_edges, from_=False)
    assert len(from_node_label) == row_count and len(to_node_label) == row_count
    df['from_schema_label'] = from_node_label
    df['to_schema_label'] = to_node_label
    for col in label_nodes:
        neighbors[col] = dfs(neighbors, col)
    return neighbors,df


def depend_step(df):
    # @params json_data: recipe data in JSON format 
    # @params df: process data model in pandas dataframe 
    # @return: dictionary of dependency relationships at Step Level
    df['dependency'] = df.apply(lambda row: list(product(row['from_schema'], row['to_schema'])),
                                             axis=1)
    dep_col = df['dependency']
    print(dep_col)
    steps_list = list(dep_col.index)
    graph_steps = graph_op_model(steps_list, dep_col)
    
    for step in steps_list:
        graph_steps[step] = list(set(dfs(graph_steps, step)))
    return graph_steps   


# save data into triples (step_id, transformation, from_schema, to_schema)
def model_process(schemas, json_data):
    trans_data = []
    for idx,schema in enumerate(schemas[1:]):
        step_id = idx+1
        cur_col_list = schema['schema']
        prev_col_list = schemas[step_id-1]['schema']
        op = json_data[idx]['op']
        if len(cur_col_list) < len(prev_col_list):
            assert op == 'core/column-removal'
            colname = json_data[idx]['columnName']
            from_node = [colname]
            to_nodes = ['null']
        elif len(cur_col_list) > len(prev_col_list):
            if op == 'core/column-split':
                from_node = [json_data[idx]['columnName']]
                to_nodes = [x for x in cur_col_list if x not in prev_col_list]
            elif op == 'core/column-addition':
                # we only consider decoding grel expression now...
                # 'expression': "grel:cells.State.value + ',' + cells.City.value"  
                #  cells["Column 1"].value + cells["Column 2"].value            
                exp = json_data[idx]['expression']
                if exp.split(':')[0] == 'grel':
                    if re.findall(r'cells.(\w+).value', exp):
                        from_node = re.findall(r'cells.(\w+).value', exp)
                    elif re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp):
                        from_node = re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp)
                    else:
                        from_node = [json_data[idx]['columnName']]
                    to_nodes = [json_data[idx]['newColumnName']]
                else:
                    from_node = [json_data[idx]['baseColumnName']]
                    to_nodes = [json_data[idx]['newColumnName']]

        elif len(cur_col_list) == len(prev_col_list):
            if cur_col_list == prev_col_list:
                from_node = [json_data[idx]['columnName']]
                to_nodes = from_node
            else:
                if op == 'core/column-rename':
                    from_node = [json_data[idx]['oldColumnName']]
                    to_nodes = [json_data[idx]['newColumnName']]
        trans_data.append((step_id, op, from_node, to_nodes))
    return trans_data


def label_status_cols(nodes_list):
    # @in: [[(a,b), (a,c)], [(b,d)],...]
    # @return: columns with labels/status, new edges pairs, neighbors for each columns
    neighbors_of = {}
    nodes = set()
    label_nodes = []
    label_edges = []
    visited_cols = {}
    for process in nodes_list:
        label_edge = []
        # init_idx=0
        for edge in process:
            u = edge[0]
            v = edge[1]
            if u not in nodes:
                label_u = f'{u}_0'
                if u != v:        
                    if v != 'null':
                        label_v = f'{v}_0'
                    else:
                        label_v = v
                else:
                    label_v = f'{v}_1' 
            else:
                # u has been recorded
                value = [i for i in visited_cols if visited_cols[i]==u]
                idx_u = int(value[-1].split('_')[-1])
                label_u = f'{u}_{idx_u}'
                if u != v:
                    if v != 'null':
                        label_v = f'{v}_{0}'
                    else:
                        label_v = v
                else:
                    label_v = f'{v}_{idx_u+1}'
            visited_cols[label_u] = u
            visited_cols[label_v] = v
            if label_u not in label_nodes:
                label_nodes.append(label_u)
            if label_v not in label_nodes:
                label_nodes.append(label_v)
            nodes.add(u)
            nodes.add(v)
            label_edge.append((label_u, label_v))
            neighbors_of.setdefault(label_u, []).append(label_v)
            # neighbors_of.setdefault(label_v, []).append(label_u)
        label_edges.append(label_edge)
    return label_edges, label_nodes, neighbors_of


def add_col_labels(label_edges, from_=True):
    # [[('Youtube_0', 'null')],...,[('State_2', 'State_3')]]
    labels = []
    for label_edge in label_edges:
        if from_:
            node_label = list(set(from_node[0] for from_node in label_edge))
        else:
            node_label = list(set(from_node[1] for from_node in label_edge))
        labels.append(node_label)
    return labels


def extract_col(operator):
    # This function is to return column node from the transformation
    # => determine the potential affected transformations and column nodes
    if isinstance(operator, str):
        op_json = json.loads(operator)
    else:
        op_json = operator
    if 'op' not in op_json:
        print('This is not a operation')
        # value-level changes can be automatically merged
        col = False
    else:
        if op_json['op'] == 'core/column-addition':  # merge operation
            exp = op_json['expression']
            if exp.split(':')[0] == 'grel':
                if re.findall(r'cells.(\w+).value', exp):
                    col = re.findall(r'cells.(\w+).value', exp)
                elif re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp):
                    col = re.findall(r'cells\[\"(\w+\s*\d*\w*)\"\]\.value', exp)
                else:
                    col = op_json['baseColumnName']
            else:
                col = op_json['baseColumnName'] 

        elif op_json['op'] == 'core/column-split':  # split operation
            col = op_json["columnName"] 
        elif op_json['op'] == 'core/column-rename':  # split operation
            col = op_json["oldColumnName"]
        elif op_json['op'] == 'core/column-removal':
            col = op_json["columnName"]
        elif op_json['op'] == 'core/column-addition-by-fetching-urls':
            col = op_json['baseColumnName']
        # elif op_json['op'] == 'core/multivalued-cell-join':
        #     col = op_json["columName"]
        elif op_json['op'] == 'core/transpose-columns-into-rows':
            col = op_json["startColumnName"]
        # elif op_json['op'] == 'core/row-removal':
        #     colname = op_json["engineConfig"]["facets"][0]["columnName"]
        # elif op_json['op'] == 'core/column-move':
        #     col = op_json["columnName"]
        elif op_json['op'] == 'core/mass-edit':
            col = op_json["columnName"]
        # elif op_json['op'] == 'core/multivalued-cell-split':
        #     col = op_json["columnName"]
        elif op_json['op'] == 'core/recon':
            col = op_json['columnName']
        else:  # normal unary operation
            try:
                col = op_json['columnName']
            except KeyError:
                col = False
        return col 

def unit_test(repair_df):
    repair_df['dependency'] = repair_df.apply(lambda row: list(product(row['from_schema'], row['to_schema'])),
                                             axis=1)
    print(repair_df['dependency'])
    # neighbors_of, nodes = find_neighbors(list(repair_df['dependency']))


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


def find_status(df, step_id, col):
    df_sub = df.head(step_id-1)
    to_schema_labels = []
    for row in df_sub[::-1].itertuples():
        if col in row.to_schema:
            to_schema_labels = row.to_schema_label
            return to_schema_labels


def return_dep_stepid(cols, df):
    stepid_list = []
    for col in cols:
        query_res = df[df.apply(lambda x: col in x.from_schema_label, axis=1)].step_id
        stepid_list.extend(query_res.tolist())
    return list(set(stepid_list))


def exe_descendants(df, dep_steps,dep_cols,mode="insert", operator=None, step_id=0):
    # @params dep_steps: dict of dependency relationships at step level
    # @params dep_cols: dict of dependency relationships at column level  
    # @params mode: ["modify", "delete", "insert"]
    # @params operator: dict of operation
    # @params step_id: row index of modified/inserted step
    # @return: affected steps list [step_id, step_id0,...], columns list [col, col_0,...]
    # Compute the affected column(s) & steps 
    col_repair = extract_col(operator) # column name without status 
    to_schema_labels = find_status(df, step_id, col_repair)
    pattern = rf'{col_repair}_\d+'
    prog = re.compile(pattern)
    for to_schema in to_schema_labels:
        if prog.match(to_schema):
            col_repair_label = to_schema
    is_exist = any((col_repair_label in i) for i in dep_cols.values())
    assert is_exist is True
    cols = dep_cols[col_repair_label] # a list of dependent columns
    if mode == 'insert':
        # all subsequent step id increase 1
        steps = return_dep_stepid(cols, df)
    else:
        # step ids do not change 
        # 1: change parameters; 2: delete operations
        steps = dep_steps[step_id]
    return steps, cols

def main1():
    mydict = { 0: [('Youtube', 'null')], 
               1: [('State', 'State')],
               2: [('County', 'County')],
               3: [('State', 'State')], 
               4: [('city', 'City')], 
               5: [('State', 'Place'), ('City', 'Place')], 
               6: [('Season1Date', 'Season1Date 1'), ('Season1Date', 'Season1Date 2'), ('Season1Date', 'Season1Date 3')],
               7: [('Season1Date 1', 'Season1Date_from')],
               8: [('Season1Date 2', 'Season1Date_to')],
               9: [('Season1Date_from', 'valid_Season1Date_from_flag')],
               10: [('Season1Date_from', 'Season1Date_from')],
               11: [('State', 'State')],
               }
    ser = pd.Series(data=mydict, index=[0,1,2,3,4,5,6,7,8,9,10,11])
    label_edges, label_nodes, neighbors = label_status_cols(list(ser))
    # print(label_nodes)
    # print(label_edges)
    print(neighbors)
    
    for col in label_nodes:
        neighbors[col] = dfs(neighbors, col)
    print(neighbors)


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
    # main()
    main1()



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