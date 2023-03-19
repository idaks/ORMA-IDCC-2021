# A helper script to inspect functions from dataset.py
from refine_pkg.OpenRefineClientPy3.google_refine.refine import refine
# project_id = 2594128575948
project_id = 1682245866457
# or_server = refine.RefineProject(refine.RefineServer(), project_id) 
# res = or_server.export_rows()
# ds_dict = list(res)
# print(ds_dict[0])

# /Users/lanli/ORMA-IDCC-2021/DTA/aux.py
from DTA.dataset import Dataset
ds = Dataset(project_id=project_id)
df= ds.read_ds()
print(df)
ds.get_index()
row_I = ds.row_I
col_J = ds.column_J
# print(row_I)
# print(col_J)
contents, structure = ds.get_model()
col_name = 'place 1'
print(df[col_name])
labels = ds.get_semantics(col_name=col_name)
print(labels)
# print(contents)
# print(structure)
# from run_sherlock import SherlockDKInjector
# sherlock_dk = SherlockDKInjector()
# sherlock_dk.initialize()
# res = sherlock_dk.exe_labels()
# print(res)

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