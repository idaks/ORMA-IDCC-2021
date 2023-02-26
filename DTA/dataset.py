import pandas as pd
from refine_pkg.OpenRefineClientPy3.google_refine.refine import refine
import numpy as np

class Dataset:
    '''
    a dataset is a collection of elements with some algebraic structure
    quintuple (Regular expression, content, structure, row_I, column_J)
    Regular expression: mining each column and return corresponding regular expression
    content: (c, lambda): c is content, map to lambda=> 2^rowindex * 3^colindex
    Structure: content : (row, column)
    row_I: row index set
    column_J: column index set
    '''

    def __init__(self, file_path=None, project_id=None):
        self.fp = file_path
        # self.df = None
        # self.row_I = []
        # self.column_J = []
        # self.content = dict()
        # self.Structure = []
        if project_id:
            self.or_server = refine.RefineProject(refine.RefineServer(), project_id) 

    def read_ds(self, ds_format='tsv'):
        """read dataset"""
        if self.fp:
            if ds_format == 'csv':
                self.df = pd.read_csv(self.fp)
            elif ds_format == 'h5':
                # HDF5 file stands for Hierarchical Data Format 5.
                self.df = pd.read_hdf(self.fp)
            elif ds_format == 'xlsx':
                self.df = pd.read_excel(self.fp)
            else:
                raise Exception('Unrecognized file format.')
        else:
            # if read from openrefine server 
            res = self.or_server.export_rows() #ds_format='tsv'
            ds_dict = list(res)
            col_schema = ds_dict[0]
            self.df = pd.DataFrame(ds_dict[1:])
            self.df.columns = col_schema
            return self.df


    def get_index(self):
        row_length = self.df.shape[0]
        column_length = self.df.shape[1]
        self.row_I = list(range(row_length))
        self.column_J = list(range(column_length))

    def get_model(self):
        # signature = 0  # lambda = pow(2,i)* pow(3,j); i:row index, j: column index
        contents = set()
        structure = []
        # pi = list()  # pairs of (row index, column index )
        for value in self.df.itertuples():
            row_id = value[0]
            element = value[1:]
            print(f'row {row_id}: value>>> {element}')
            for i, e in enumerate(element):
                print(f'column index: {i} >>>> data value:{e}')
                pos = (row_id, i)  # coordinates of cell
                signature = pow(2, row_id) * pow(3, i)
                contents.add((e, signature))
                structure.append({e: pos})
                # pi.append(pos)
        return sorted(contents, key=lambda x: x[1]),structure

    def get_regex(self,old_col, new_col):
        # sherlock?
        # TODO
        
        pass
