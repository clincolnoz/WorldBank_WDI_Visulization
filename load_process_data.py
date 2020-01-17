# -*- coding: utf-8 -*-
#%%
import os
import numpy as np
import pandas as pd
import zipfile

root_dir = os.path.dirname(os.path.abspath(__file__))
if len(os.listdir(os.path.join(root_dir,'data/')))==1:
    with zipfile.ZipFile("data.zip","r") as zip_ref:
        zip_ref.extractall(os.path.join(root_dir,'data/'))



def load_data():
    wdi_indicator_code_name_topic = pd.read_csv(os.path.join(root_dir,'data/wdi_indicator_code_name_topic.csv'),index_col='Indicator Name')
    wdi_country_code_name = pd.read_csv(os.path.join(root_dir,'data/wdi_country_code_name.csv'))
    wdi_country = pd.read_csv(os.path.join(root_dir,'data/WDICountry.csv'),index_col='Table Name')
    wdi_country.index.set_names('Country Name',inplace=True)

    wdi = pd.read_csv(os.path.join(root_dir,'data/wdi_small.csv'),index_col=['Country Name','Indicator Name'])
    wdi_pivot = pd.read_csv(os.path.join(root_dir,'data/wdi_pivot.csv'),index_col='Country Name')
    wdi_pivot=wdi_pivot.join(wdi_country['Region'])
    wdi_pivot.Region = wdi_pivot.Region.fillna('AGG')
    corr_matrix = pd.read_csv(os.path.join(root_dir,'data/corr_matrix.csv'),index_col='Indicator Name')
    corr_matrix_sign = pd.read_csv(os.path.join(root_dir,'data/corr_matrix_sign.csv'),index_col='Indicator Name')
    corr_sig_matrix = pd.read_csv(os.path.join(root_dir,'data/corr_sig_matrix.csv'),index_col='Indicator Name')
    
    return wdi_indicator_code_name_topic, wdi_country_code_name, wdi_country, wdi, wdi_pivot, corr_matrix, corr_matrix_sign, corr_sig_matrix



