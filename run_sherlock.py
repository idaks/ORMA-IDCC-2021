from sherlock_project.sherlock import helpers
from sherlock_project.sherlock.deploy.model import SherlockModel
from sherlock_project.sherlock.functional import *
from sherlock_project.sherlock.features.paragraph_vectors import initialise_pretrained_model, initialise_nltk
from sherlock_project.sherlock.features.preprocessing import (
    extract_features,
    # convert_string_lists_to_lists,
    prepare_feature_extraction,
    # load_parquet_values,
)
from sherlock_project.sherlock.features.word_embeddings import initialise_word_embeddings
import pandas as pd 
import numpy as np

class SherlockDKInjector():
    """
    The domain-knowledge inferred by Sherlock
    Deep Learning system 
    """
    def __init__(self):

        """Initialize spacy"""
        # self.nlp = spacy.load('en_core_web_lg')
        
        helpers.download_data() # Downloading the raw data into ../data/.
        prepare_feature_extraction() # Preparing feature extraction by downloading 4 files ../sherlock/features/
        initialise_word_embeddings()
        initialise_pretrained_model(400) # 400 => dimension 
        initialise_nltk()
        print("sherlock loaded...")  # check how much memory it takes up... --> 14312 MiB
        # time.sleep(10)

    def exe_labels(self, col_values_list=None,temp_f='Features/temporary_1.csv'):
        """
        Args:
            col_values_list: list of values in a column 
        Returns:
            predicted_label: semantic data type
        """
        # data = pd.Series([col_values_list], name='values')
        data = pd.Series(
            [
                ["Jane Smith", "Lute Ahorn", "Anna James"],
                ["Amsterdam", "Haarlem", "Zwolle"],
                ["Chabot Street 19", "1200 fifth Avenue", "Binnenkant 22, 1011BH"]
            ],
            name="values"
        )
        # predicted_label = self.train_test_sherlock("Features/temporary_1.csv", data)
        extract_features(
            temp_f,
            data
        )
        feature_vectors = pd.read_csv(temp_f, dtype=np.float32)
        print(feature_vectors)
        # init sherlock
        self.model = SherlockModel()
        self.model.initialize_model_from_json(with_weights=True, model_id="sherlock")
        predicted_labels = self.model.predict(feature_vectors, "sherlock")
        return predicted_labels