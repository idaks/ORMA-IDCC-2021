# idcc2021

#Workflow: Reproduce the data cleaning task in usecase1
1. Running OpenRefine server http://127.0.0.1:3333/
2. Create a Project by Loading project_files/Menu.openrefine.tar.gz;
   If you have already had one project for analysis, skip this step.
3. copy the project id from step 2

4. A "run-bash" that executes the views:
Parameters:
     project id, 
     output gv file path/name, 
     command {'modular_views', 'schema_views', 'parallel_views', 
    'table_view'}

Bash Command:
   `python main.py --project_id [Project ID] --output [Output file path] command {'modular_views', 'schema_views', 'parallel_views', 
'table_view'}`


We have four subfolders for saving views by these four commands: 

1. modular_views - sub-workflows of parallel views 
2. parallel_view - workflow view with column-level dependency relationship
3. schema_view - workflow view at schema level
4. table_view - workflow view at table level
