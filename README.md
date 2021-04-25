# idcc2021

Workflow of using ORMA

1. Download/Clone ORMA 

     `git clone https://github.com/idaks/ORMA-IDCC-2021`

2. Download OpenRefine Python Client library Dependency

     `cd ORMA-IDCC-2021`
     
     `cd refine_pkg`
     
     `git clone https://github.com/LanLi2017/OpenRefineClientPy3`


3. Check your graphviz version:
   
   Example:
   
     `dot -V`
  
     `dot - graphviz version 2.42.3 (20191010.1750)`
      
   If you don't have dot installed. Install the latest version Download **[graphviz](<https://www.graphviz.org/download/)

    1). For Mac users (ex.use Homebrew):
    
    `$ brew install graphviz`
    
    2). For Windows users, choose one of the methods from the **[download](<https://www.graphviz.org/download/) website
    
    3). For Linux users, choose one of the methods from the **[download](<https://www.graphviz.org/download/)* website
    
    
4. Change run.bash to run main.py (Please refer to README.md in usecase1 folder)