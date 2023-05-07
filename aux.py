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



def send_gpt_prompts_with_ret(all_query_tuples_serialized, the_encoder, the_tokenizer, missing_att,
                            reranker_type = None, index_name = "es_index_1", index_type = "ES", object_imp = "object"):
    ### GPT3.5 Params
    service_name = "dataprepopenai2"
    deployment_name = "retclean_gpt35"#"retclean_gpt35"
    key = "5b8e613900314c6e95839d5509fbea80"  # please replace this with your key as a string

    openai.api_key = key
    openai.api_base =  "https://{}.openai.azure.com/".format(service_name) # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
    openai.api_type = 'azure'
    openai.api_version = '2022-06-01-preview' # this may change in the future

    deployment_id=deployment_name #This will correspond to the custom name you chose for your deployment when you deployed a model. 

    if reranker_type != None:
        reranker_model = load_encoder_reranker(mode=reranker_type)

    # 2D list for results of each query tuple
    all_final_results = []
    for i in range(len(all_query_tuples_serialized)):
        temp_results = []

        query_tuple = all_query_tuples_serialized[i]
        # print(query_tuple, "\n\n")

        retrieved = search_index(query_tuple, # str format, serialized
                            "./tmp/aggregation_{}.csv".format(index_name),
                            "./faiss_index/", 
                            index_name, #es_attempt_2 for es ,  faiss_attempt_4 for faiss
                            the_encoder,
                            the_tokenizer,
                            index_type = index_type,
                            k = 3 # number of tuples to retrieve
                            )
        # print(retrieved, "\n\n")

        if reranker_type == "colbert":
            retrieved = colbert_like_rerank(query_tuple, retrieved, reranker_model)
        elif reranker_type == "crossencoder":
            retrieved = cross_encoder_based_rerank(query_tuple, retrieved, reranker_model)

        for j in range(3):
            ret = retrieved["serialization"][j]
            # missing_att
    #org prompts        # prompt="<|im_start|>system\nThe system is an AI assistant answer questions based on the information in the promot.\n<|im_end|>\n<|im_start|>user\nTuple 1 = {} Tuple 2 = {} Are Tuple 1 and Tuple 2 talking about the exact same entity. If yes, then what should be the {} value for Tuple 1 based on Tuple 2? If the 2 tuples are not about the exact same entity answer with 'No'. \n<|im_end|>\n<|im_start|>assistant".format(query_tuple, ret, missing_att)
            prompt="<|im_start|>system\nThe system is an AI assistant answer questions based on the information in the 2 Tuples provided. Only answer Question 2 if you answer yes to Question 1. If your answer to Question 1 in 'no', response with that.\n<|im_end|>\n<|im_start|>user\nTuple 1 = {} Tuple 2 = {}. Question 1: Are Tuple 1 and Tuple 2 about the same {}, yes or no? Question 2: If your answer to Question 1 was yes, then determine what the {} value for Tuple 1 should be based on Tuple 2? \n<|im_end|>\n<|im_start|>assistant".format(query_tuple, ret, object_imp, missing_att)
            ## Send GPT3.5 Request
            response1 = openai.Completion.create(engine="gpt3_davinci_imputer", prompt=prompt,
                                        temperature=0.1,
                                        max_tokens=32,
                                        top_p=0.95,
                                        frequency_penalty=0.5,
                                        presence_penalty=0.5,
                                        stop=["<|im_end|>"])
            # print(prompt)
            # print(response1["choices"][0]["text"])
            temp_results.append({
                "repair" : response1["choices"][0]["text"],
                "source" : ret,
                "table" : retrieved["table"][j],
                "index" : retrieved["index"][j]
            })
            time.sleep(0.5)
        # print(temp_results, "\n\n")
        all_final_results.append(temp_results)

    # Keep First Positive Responses Only for Each Query Tuple
    all_final_results_positive_only = keep_first_positive_response(all_final_results)

    # Extract Answers
    all_final_results_positive_only_post_processed = answer_extraction_from_response(all_final_results_positive_only,missing_att)


    return all_final_results_positive_only_post_processed
