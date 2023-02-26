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

##### Use case 1: Modify the parameters of `Split Column` transformation
> Check the graph: demo.md[https://github.com/idaks/ORMA-IDCC-2021/blob/model-analysis/demo.md]

