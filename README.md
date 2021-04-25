# idcc2021

Workflow of using ORMA

1. Download/Clone ORMA 

     `git clone https://github.com/idaks/ORMA-IDCC-2021`

2. Download OpenRefine Python Client library Dependency

     `cd ORMA-IDCC-2021`
     
     `cd refine_pkg`
     
     `git clone https://github.com/LanLi2017/OpenRefineClientPy3`


3. Check your graphviz version:

     `dot -V`
  
     `dot - graphviz version 2.42.3 (20191010.1750)`
      
   a. Install the latest version Download _`Graphviz <https://www.graphviz.org/download/>`_

    1). For Mac users (ex.use Homebrew):
    
    `$ brew install graphviz`
    
    2). For Windows users, choose one of the methods from the _`download <https://www.graphviz.org/download/>`_website
    
    3). For Linux users, choose one of the methods from the _`download <https://www.graphviz.org/download/>`_ website
    
    
4. Change run.bash to run main.py (Please refer to README.md in usecase1 folder)