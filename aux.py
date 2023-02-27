# A helper script to inspect functions from dataset.py
from refine_pkg.OpenRefineClientPy3.google_refine.refine import refine
project_id = 2594128575948
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
print(row_I)
print(col_J)
contents, structure = ds.get_model()
print(contents)
print(structure)
