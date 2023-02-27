# idcc2021

ORMA case study: Recipe Update problem

#### Description: 
Given a chain of data transformations {op0,op1,op2,..opn}, data cleaners/curators figure out there are missing steps in between or they miused some parameters with old steps. Recipe update problem is requires to be fixed by allowing inserting new steps, or replacing the old steps with new steps at the location of errors. 

##### Two ways of modification/update:
- [x] Add new operation(s)
- [x] Modify old operation(s)

Contextual Information 
: Preconditions
- With the help of ORMA, we could get two layers of dependency informations: 
   > Dependency relationships at column level;
   > Dependency relationships at step/operation level;
- With the help of DTA (Data Transformation Algebra), we could execute how data transformations perform on the data mdoels 
     > Dataset model:  D = (R, L, S, I, J)
     1. R: Regular expression across the column
     2. L: `{(data values, signature),...}`. A collection of pairs of data contents; signature: a unique identifier to descipe the location of data value. 
     3. S: `[{data values: (row index, column index)},..]`. Structure information: for each data value,its row index and column index
     4. I: a collection of row indices; J: a collection of column indices

##### Challenges
1. Use DTA to return how this transformation perform on the dataset: {*rigid transformation*, *geometric transformation*}
> rigid transformation: only change data value at the cell level;

> geometric transformation: change both data values and structure information. E.g., schema information,...
2. Different types of transformation can be inheriant/ can influence the following graph/steps differently.
> value level: can be connected directly

> schema level: in order to replace the old nodes/steps from the original graph with the new nodes/steps, value-level matching and mapping are required. 
3. How to update the transformation(s)nodes from the old graph that are dependent on the **repaired**/**updated** transformation(s)?
> DTA requires to be advanced not only cover the regular expression from syntactic level, but we should focus on data semantic types. By matching and mapping the semantic data types between **repaired**/**updated** transformation(s) and dependent nodes, we could finalize the graph merge. 
In details: the dependent transformation(s)/nodes will be updated correspondingly
> Advanced Dataset model:  `D = (R, L, S, I, J, T)` (T: semantic data types) 

#### Methods
1. Use OpenRefine Python Client Library[https://github.com/LanLi2017/OpenRefineClientPy3] to connect with OpenRefine server. Through undo/redo, we could get internal data products/ dataset versions during the data cleaning process. 
2. Data model developed by DTA (Data Transformation Algebra) from paper "A first-principles algebraic approach to data transformations in data cleaning: understanding provenance from the ground up"[https://www.usenix.org/system/files/tapp2020-paper-nunez-corrales.pdf]. 
`cited as {Núnez-Corrales, S., Li, L., & Ludäscher, B. (2020, June). A first-principles algebraic approach to data transformations in data cleaning: understanding provenance from the ground up. In Proceedings of the 12th USENIX Conference on Theory and Practice of Provenance (pp. 3-3).}`
3. Advanced data model based on DTA by providing semantic data types supported by Sherlock: "Sherlock
A Deep Learning Approach to Semantic Data Type Detection"[https://github.com/mitmedialab/sherlock-project].
`cited as {Madelon Hulsebos, Kevin Hu, Michiel Bakker, Emanuel Zgraggen, Arvind Satyanarayan, Tim Kraska, Çağatay Demiralp, and César Hidalgo. 2019. Sherlock: A Deep Learning Approach to Semantic Data Type Detection. In The 25th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’19), August 4–8, 2019, Anchorage, AK, USA. ACM, New York, NY, USA, 9 pages. https://doi.org/10.1145/3292500.3330993}`

##### Use case 1: Modify the parameters of `Split Column` transformation
> Check the graph: demo.md[https://github.com/idaks/ORMA-IDCC-2021/blob/model-analysis/demo.md]

