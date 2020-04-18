import pandas as pd
import numpy as np
import pingouin as pg

from sklearn.preprocessing import StandardScaler


dataDir = './data/'

# TODO: download this from the website if it doesn't exist locally
wdi = pd.read_csv(dataDir+'WDIData.csv')
wdi.drop('Unnamed: 64',axis=1,inplace=True)

# build seperate df with codes and names for indicator (to join back later)
wdi_indicator_code_name = wdi[['Indicator Code','Indicator Name']].drop_duplicates()
wdi_indicator_code_name.set_index('Indicator Name', inplace=True)
wdi_indicator_code_name.index.set_names('Indicator Name', inplace=True)

# build seperate df with codes and names for indicator (to join back later)
wdi_country_code_name = wdi[['Country Code','Country Name']].drop_duplicates()
wdi_country_code_name.set_index('Country Name', inplace=True)
wdi_country_code_name.index.set_names('Country Name', inplace=True)

# Set index to codes and drop names
wdi.set_index(['Country Name','Indicator Name'], inplace=True)
wdi.index.set_names(['Country Name','Indicator Name'], inplace=True)
wdi.drop(['Country Code','Indicator Code'],axis=1,inplace=True)
# Set years as integer
wdi.columns = wdi.columns.astype(int)

# Take just 1990 on
wdi = wdi.loc[:,wdi.columns>=1990]


index_to_drop = wdi_indicator_code_name.reset_index().set_index(['Indicator Code']).filter(regex=r'\.MA|\.FE',axis=0).reset_index().set_index('Indicator Name').index
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'% net',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'PPP',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'annual \% growth',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'constant 2010 US',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'\% of GNI',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'constant LCU',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'current LCU',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'quintile',axis=0).index)
index_to_drop = index_to_drop.union(wdi_indicator_code_name.filter(regex=r'gender parity index (GPI)',axis=0).index)


wdi_small=wdi.reset_index().set_index('Indicator Name').drop(index_to_drop,axis=0).reset_index().set_index(['Country Name','Indicator Name']).copy()



print('Number of unique indicators (raw): ' + str(wdi.index.get_level_values(1).unique().shape[0]))
print('Number of unique indicators (small): ' + str(wdi_small.index.get_level_values(1).unique().shape[0]))
print('Number of unique countries and agg: ' + str(wdi_small.index.get_level_values(0).unique().shape[0]))
print('Number of records: ' + str(wdi_small.shape[0]*wdi_small.shape[1]))
print('Number of records of which are NaN: ' + str(wdi_small.isna().sum().sum()))
print('Leaving: ' + str(wdi_small.shape[0]*wdi_small.shape[1]-wdi_small.isna().sum().sum()))


wdi_code_breakdown = pd.read_csv(dataDir+'WDISeries.csv')

wdi_code_breakdown['indicator_prefix']=wdi_code_breakdown['Series Code'].str.split('.',expand=True)[0]
wdi_code_breakdown['topic_prefix'] = wdi_code_breakdown.Topic.str.split(':',expand=True)[0]

print(wdi_code_breakdown.topic_prefix.unique())

wdi_indicator_code_name_topic = wdi_indicator_code_name.merge(wdi_code_breakdown,left_on='Indicator Code',right_on='Series Code')
wdi_indicator_code_name_topic = wdi_indicator_code_name_topic[['Indicator Code','topic_prefix','Indicator Name']].set_index('Indicator Name')


wdi_pivot = wdi_small.loc[:,wdi.columns>=1990].mean(axis=1).rename('mean').reset_index().copy()
wdi_pivot = wdi_pivot.pivot(index='Country Name',columns='Indicator Name',values='mean')
wdi_pivot_scaled = pd.DataFrame(StandardScaler().fit_transform(wdi_pivot.fillna(wdi_pivot.median())),index=wdi_pivot.index,columns=wdi_pivot.columns)

corr_matrix = wdi_pivot_scaled.corr()
corr_matrix_sign = np.sign(corr_matrix)
corr_matrix = corr_matrix.abs()
corr_sig_matrix=wdi_pivot_scaled.fillna(wdi_pivot.median()).rcorr(decimals=2)

wdi_small.to_csv('data/wdi_small.csv',index=True)
wdi_pivot.to_csv('data/wdi_pivot.csv',index=True)
corr_matrix.to_csv('data/corr_matrix.csv',index=True)
corr_matrix_sign.to_csv('data/corr_matrix_sign.csv',index=True)
corr_sig_matrix.to_csv('data/corr_sig_matrix.csv',index=True)
wdi_code_breakdown.to_csv('data/wdi_code_breakdown.csv',index=True)
wdi_indicator_code_name_topic.to_csv('data/wdi_indicator_code_name_topic.csv',index=True)
wdi_country_code_name.to_csv('data/wdi_country_code_name.csv',index=True)
