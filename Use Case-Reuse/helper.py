# This script is to help improve the reusability of data transformations 
# use column-split as an example
import pandas as pd
import logging

# FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
logging.basicConfig(filename='split_col.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def return_col_names():
    # This function is to predict column name based on data values [semantic-level]
    # @in: dataframe with new columns 
    # @return: column name [e.g., 'city', 'state',...]
    '''method 1: Sherlock prediction''' 
    


    '''method 2: chat gpt'''
    pass


# Method 1: replace and eable the separators consistent
def split_adv1(sep, col_name, df:pd.DataFrame, thread=0.2):
    # for sep in seps:
    # df_new = df[col_name].str.split(sep, expand=True)
    # sum_rows = df_new.shape[0]
    # # Filter the rows that contain missing values
    # filtered_df = df_new[df_new.isnull().any(axis=1)]
    # num_rows = filtered_df.shape[0]
    # if num_rows/sum_rows <= thread:
    #     return df_new
    # else:
        
    #     pass
    pass


# Method 2: continue trying separators to split
def split_adv2(sep, col_name, df:pd.DataFrame):
    df_new = df[col_name].str.split(sep, expand=True)
    # Filter the rows that contain missing values
    failed_idx = df_new[df_new.isnull().any(axis=1)].index.tolist()
    correct_df = df_new[~df_new.isnull().any(axis=1)]
    #TODO： should be more strict: check if non-word characters existing here?
    logging.info(f'Append rows: {correct_df}')

    return correct_df, failed_idx


def main():
    # Create a sample DataFrame
    seps = [',', ';']
    col_name = 'Location' 
    data = {'Location': ['Chicago,IL', 'Seattle,WA', 'Evansville,IN', 'Denver,CO',
                        'Hampton,VA', 'New York;NY', 'Newark;NJ', 'San Jose;CA', 
                        'Portland;OR', 'Overland Park;KS']
            }
    df = pd.DataFrame(data)
    df_cp = df.copy()
    df_clean_m1 = pd.DataFrame()
    df_clean_m2 = pd.DataFrame()
    for sep in seps:
        if not df_cp.empty:
            correct_df, failed_idx = split_adv2(sep, col_name, df_cp)
            df_cp = df_cp.loc[failed_idx].copy()
            print(correct_df)
            df_clean_m2 = df_clean_m2.append(correct_df, ignore_index=True)
            # num_rows = df_cp.shape[0]
            sum_rows = df.shape[0]
            logging.info(f'Using separator `{sep}`,\n Failed percentage: {len(failed_idx)/sum_rows*100}...')
            logging.info(f'Failed dataframe: {df_cp}')
            logging.info(f'Current Dataframe Using Separator {sep}: \n\
                        {df_clean_m2}')
    if not df_cp.empty:
        num_rows_left = df_cp.shape[0]
        logging.info(f'There are still {num_rows_left} rows left that \
                        cannot be resolved by current available separators.')
        logging.info(f'Failed dataframe: {df_cp}')
        df_clean_m2 = df_clean_m2.append(df_cp, ignore_index=True)
    
    combined_df = pd.concat([df, df_clean_m2], axis=1)
    logging.info('Rows appended sucessfully.')

    # Display the resulting dataframe
    logging.info(f'Resulting DataFrame By Method 2:\n{combined_df}')


if __name__ == '__main__':
    main()