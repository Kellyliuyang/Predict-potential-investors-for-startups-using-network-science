import pandas as pd
import numpy as np
import datetime
import itertools
from collections import Counter

organizations = pd.read_csv('organizations.csv',low_memory=False)
funding_rounds = pd.read_csv('funding_rounds.csv',low_memory=False)
investments = pd.read_csv('investments.csv',low_memory=False)
investors = pd.read_csv('investors.csv',low_memory=False)

organizations['founded_on'] = pd.to_datetime(organizations['founded_on'],format = '%Y-%m-%d',errors = 'coerce')
organizations['last_funding_on'] = pd.to_datetime(organizations['last_funding_on'],format = '%Y-%m-%d',errors = 'coerce')
funding_rounds['announced_on'] = pd.to_datetime(funding_rounds['announced_on'],format = '%Y-%m-%d',errors = 'coerce')

# filter
organization2 = organizations.loc[organizations.country_code.isin(['USA'])]
organization2 = organization2.loc[organizations.primary_role.isin(['company'])]
#organization2 = organization2.loc[organizations.status.isin(['operating'])]
start_date = datetime.datetime(2012,1,1)
end_date = datetime.datetime(2018,1,1)
mask = (organization2['founded_on'] >= start_date) & (organization2['founded_on'] < end_date)
organization2 = organization2.loc[mask]
#organization2 = organization2.loc[organization2['last_funding_on'] >= '2017-1-1']

# merge funding round table
funding_rounds2 = funding_rounds.loc[funding_rounds.company_uuid.isin(organization2.uuid)]
funding_rounds3 = funding_rounds2.merge(investments,on='funding_round_uuid', how='inner')
funding_rounds4 = funding_rounds3.merge(investors, left_on='investor_uuid', right_on='uuid', how='inner')
funding_rounds4 = funding_rounds4[['company_name','company_uuid','investor_name','investor_uuid','announced_on']].drop_duplicates().dropna()

# test dataset
date1=datetime.datetime(2013,1,1)
date2=datetime.datetime(2018,1,1)
mask2 = (funding_rounds4['announced_on'] >= date1) & (funding_rounds4['announced_on'] < date2)
funding_rounds12_16=funding_rounds4.loc[mask2]
testing = funding_rounds4.loc[funding_rounds4['announced_on'] >= date2]

# company-company
investors_l = list(funding_rounds12_16['investor_uuid'].drop_duplicates())
uw_coinvestment2 = []
for inv in investors_l:
    inv_funding = funding_rounds12_16.loc[funding_rounds12_16['investor_uuid'] == inv]
    inv_companies = list(inv_funding['company_uuid'].drop_duplicates())

    # Possible combinations between the investors, which is the co-investment relationship introduced by investing in this company.
    temp_coinvestment2 = list(itertools.combinations(inv_companies,2))
    uw_coinvestment2.extend(temp_coinvestment2)

#  Get the weighted co-investment relationship between two companies
#  Regardless of the sequence, look at the frequencies a certain combination of investors happened in our unweighted list of co-investment.
w_coinvestment2 = Counter([[(b, a), (a, b)][a < b] for a, b in uw_coinvestment2])

#  Normalize the co-investment by the number of investment by a company
#  The number of times an company uuid appears in our funding_rounds12_16 dataframe
company_investments = list(funding_rounds12_16['company_uuid'])
num_company_investment = Counter(company_investments)

source2 = []
target2 = []
weight2 = []
normalize2 = []
for key2, count2 in w_coinvestment2.items():
    temp_source2, temp_target2 = key2

    source2.append(temp_source2)
    target2.append(temp_target2)
    weight2.append(count2)
    normalize_source2 = num_company_investment.get(temp_source2)
    normalize2.append(normalize_source2)

    source2.append(temp_target2)
    target2.append(temp_source2)
    weight2.append(count2)
    normalize_target2 = num_company_investment.get(temp_target2)
    normalize2.append(normalize_target2)

d = {'company1': source2, 'company2': target2, 'Num of Co-investors': weight2, 'Num of Investors of company1': normalize2}
df = pd.DataFrame(d)
df['Company edges weight'] = df['Num of Co-investors']/df['Num of Investors of company1']

funding_rounds12_162 = funding_rounds12_16.groupby(['company_uuid','investor_uuid']).count().reset_index()
funding_rounds12_162= funding_rounds12_162[['company_uuid','investor_uuid','announced_on']]
funding_rounds12_162.columns=['company_uuid','investor_uuid','investment_times']
#df2=funding_rounds12_162.merge(df, how='inner', right_on='company2', left_on='company_uuid')

been_invested = funding_rounds12_16.groupby(['company_uuid']).count().reset_index()
been_invested= been_invested[['company_uuid','investor_uuid']]
been_invested.columns=['company_uuid','been_invested_times']

been_invested = funding_rounds12_16.groupby(['company_uuid']).count().reset_index()
been_invested= been_invested[['company_uuid','investor_uuid']]
been_invested.columns=['company_uuid','been_invested_times']

normalized_investment=funding_rounds12_162.merge(been_invested, how='left', on='company_uuid')
normalized_investment['normalized_investment']=normalized_investment['investment_times']/normalized_investment['been_invested_times']
normalized_investment=normalized_investment[['company_uuid','investor_uuid','normalized_investment']]
#normalized_investment.to_csv('normalized_investment13_17.csv')

df2=normalized_investment.merge(df, how='inner', right_on='company2', left_on='company_uuid')
df2['sub_score']=df2['Company edges weight']*df2['normalized_investment']
df3=df2.groupby(['company1','investor_uuid']).sum().reset_index()
df3=df3[['company1','investor_uuid','sub_score']]
df3.columns=['company_uuid', 'investor_uuid', 'score']

#feature selection
company_feature=organization2[['uuid','state_code','status','funding_rounds']]
company_feature.columns=['company_uuid','state_code','status','funding_rounds']
#'category_group_list'
#investor feature
investor_feature=investors[['uuid','state_code','investor_type','investment_count']]
investor_feature.columns=['investor_uuid','state_code','investor_type','investment_count']

company_score_i=pd.read_csv('/Users/yangliu/Documents/586 final project/DATA/csv_export/Company Score from Investor Network13_17.csv')
company_score_i.columns=['company_uuid','investor_uuid','company_score_i']

community=pd.read_csv('/Users/yangliu/Documents/586 final project/nodeModularity13_17.csv')
company_community=community.loc[community.nodetype=='Company']
company_community=company_community[['Id','modularity_class']]
company_community.columns=['company_uuid','modularity_class1']
investor_community=community.loc[community.nodetype=='Investor']
investor_community=investor_community[['Id','modularity_class']]
investor_community.columns=['investor_uuid','modularity_class2']
community2=df3.merge(company_community,how='left',on='company_uuid').merge(investor_community,how='left',on='investor_uuid')
community3=community2.loc[community2.modularity_class1==community2.modularity_class2]
community3['community'] = 1
community4=community2.loc[~community2.index.isin(community3.index)]
community4['community'] = 0
community_df=pd.concat([community3,community4],axis=0)
community_df=community_df[['company_uuid','investor_uuid','community']]

gaint_component=pd.read_csv('/Users/yangliu/Documents/586 final project/giant_component13_17.csv')
gaint_component=gaint_component[['Source','Target']]
gaint_component.columns=['investor_uuid','company_uuid']
testing2 = testing.loc[(testing.company_uuid.isin(gaint_component.company_uuid))&(testing.investor_uuid.isin(gaint_component.investor_uuid))]
testing2=testing2[['company_uuid','investor_uuid','announced_on']]

test_data1 = testing2.merge(df3, how='left',on=['company_uuid','investor_uuid'])
test_data = test_data1.merge(company_score_i, how='left',on=['company_uuid','investor_uuid'])
test_data = test_data[['company_uuid','investor_uuid','announced_on', 'score','company_score_i']]
# label is 1
testing1=test_data.dropna()
testing1=testing1.drop('announced_on',axis=1)
testing1['label']=1

#label is -1
test_y=df3.merge(testing, how='inner',on=['company_uuid','investor_uuid']).dropna()
test_n=df3.loc[~df3.index.isin(test_y.index)]
left_data=test_n.merge(gaint_component, how='inner',on=['company_uuid','investor_uuid'])

#company score i
test_data = test_data1.merge(company_score_i, how='left',on=['company_uuid','investor_uuid'])
test_data = test_data[['company_uuid','investor_uuid','announced_on', 'score','company_score_i']]
testing2 = left_data.merge(company_score_i, how='left',on=['company_uuid','investor_uuid']).dropna()
testing2['label']=-1
testing_2=testing2.sample(n=len(testing1))
testing_data = pd.concat([testing1,testing_2],axis=0)

weight=pd.read_csv('/Users/yangliu/Documents/586 final project/DATA/csv_export/normalized_investment13_17.csv')
weight=weight.drop('Unnamed: 0',axis=1)
testing_data.investor_uuid=testing_data.investor_uuid.astype(str)
testing_data_feature=testing_data.merge(weight,how='left',on=['company_uuid','investor_uuid']).fillna(0)
testing_data_feature=testing_data_feature.merge(community_df,how='left',on=['company_uuid','investor_uuid']).dropna()
#eigenvector
inv_ev=pd.read_csv('/Users/yangliu/Documents/586 final project/inv_EV13_17.csv')
comp_ev=pd.read_csv('/Users/yangliu/Documents/586 final project/comp_EV13_17.csv')
testing_data_feature=testing_data_feature.merge(inv_ev,how='left',on='investor_uuid')
testing_data_feature=testing_data_feature.merge(comp_ev,how='left',on='company_uuid')
#company investor feature
testing_data_feature=testing_data_feature.merge(company_feature,how='left',on='company_uuid')
testing_data_feature=testing_data_feature.merge(investor_feature,how='left',on='investor_uuid')

testing_data_feature.to_csv('/Users/yangliu/Documents/586 final project/test2018_2.csv',index=False)






