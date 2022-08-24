import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.write("""
    # Salary Prediction App


    This app helps data scientist/analyst to negotiate their income for an existing or a new job
    """
         )
st.header('**please enter the following details**')

founded_year_list = []
def for_founded_year(founded_year_list):
     for i in range(1700,2050,1):
         founded_year_list.append(i)

for_founded_year(founded_year_list)

company_competitors_list = [0,1,2,3,4]

sector_columns = ['Biotech & Pharmaceuticals', 'Health Care',
                    'Business Services','Information Technology','Others']

ownership_list = ['Private','Others']

job_title_list = ['Data Scientist' , 'Data Analyst' , 'Others']

def user_input_features():
    company_rating = st.slider("What is company's rating?" , 0.00,3.00,5.00)
    company_founded = st.selectbox('Select the founded year', founded_year_list)
    competitors = st.selectbox("Select company's competitors number", company_competitors_list)
    sector = st.selectbox("Select company's sector",sector_columns)
    ownership = st.selectbox("Select company's ownership",ownership_list)
    job_title = st.selectbox("Select your job title",job_title_list)
    job_in_headquarters = st.selectbox("Is your job in headquarters?",['Yes','No'])
    job_seniority=st.selectbox("What's your job position",['Senior','Junior','Other'])
    st.write("Your skills?")
    excel=st.checkbox('Excel')
    python=st.checkbox('Python')
    tableau=st.checkbox('Tableau')
    SQL=st.checkbox('SQL')
    skills_list = []
    if excel==1:
        skills_list.append('Excel')
    if python==1:
        skills_list.append('Python')
    if tableau==1:
        skills_list.append('Tableau')
    if SQL==1:
        skills_list.append('SQL')


    data = {'company_rating': company_rating, 'company_founded':company_founded,'competitors':competitors,
            'sector':sector,'ownership':ownership,'job_title':job_title,'job_in_headquarters':
             job_in_headquarters,'job_seniority':job_seniority,'job_skills': (",").join(skills_list)
            }
    features = pd.DataFrame(data,index=[0])
    return features


input_df = user_input_features()
st.write("The details you have entered")
st.write(input_df)

model = pickle.load(open('salary_prediction_model.pickle','rb'))

df = pd.read_csv('glassdoor_jobs.csv')
df['Rating']=df['Rating'].apply(lambda x: np.NaN if x==-1 else x)
df['Rating']=df['Rating'].fillna(df['Rating'].mean())

df['Founded']=df['Founded'].apply(lambda x: np.NaN if x==-1 else x)
df['Founded']=df['Founded'].fillna(df['Founded'].median())

from sklearn.preprocessing import StandardScaler

sc_rating = StandardScaler()
sc_rating.fit_transform(df[['Rating']])

sc_founded = StandardScaler()
sc_founded.fit_transform(df[['Founded']])

def predict_salary(rating, founded, competitors, sector, ownership, job_title, job_seniority,job_in_headquarters,
                   job_skills):

    prediction_input = list()

    prediction_input.append(sc_rating.transform(np.array(rating).reshape(1, -1)))
    prediction_input.append(sc_founded.transform(np.array(founded).reshape(1, -1)))
    prediction_input.append(int(competitors))

    sector_columns = ['Biotech & Pharmaceuticals', 'Health Care',
                      'Business Services', 'Information Technology']
    temp = list(map(int, np.zeros(shape=(1, len(sector_columns)))[0]))
    for index in range(0, len(sector_columns)):
        if sector_columns[index] == sector:
            temp[index] = 1
            break
    prediction_input = prediction_input + temp

    if ownership == 'Private':
        prediction_input.append(1)
    else:
        prediction_input.append(0)

    job_title_columns = ['Data Scientist', 'Data Analyst']
    temp = list(map(int, np.zeros(shape=(1, len(job_title_columns)))[0]))
    for index in range(0, len(job_title_columns)):
        if job_title_columns[index] == job_title:
            temp[index] = 1
            break
    prediction_input = prediction_input + temp

    job_seniority_map = {'Other': 0, 'Junior': 1, 'Senior': 2}
    prediction_input.append(job_seniority_map[job_seniority])

    job_in_headquarters_map = {'Yes': 1, 'No': 0}
    prediction_input.append(job_in_headquarters_map[job_in_headquarters])

    temp = list(map(int, np.zeros(shape=(1, 4))[0]))
    if 'Excel' in job_skills:
        temp[0] = 1
    if 'Python' in job_skills:
        temp[1] = 1
    if 'Tableau' in job_skills:
        temp[2] = 1
    if 'SQL' in job_skills:
        temp[3] = 1
    prediction_input = prediction_input + temp
    return model.predict([prediction_input])[0]


salary = predict_salary(input_df['company_rating'][0],input_df['company_founded'][0],input_df['competitors'][0],
                        input_df['sector'][0],input_df['ownership'][0],input_df['job_title'][0],
                        input_df['job_seniority'][0],input_df['job_in_headquarters'][0],input_df['job_skills'][0]
                        )

st.header('The predicted salary ')
st.write('Estimated salary (range): {}(USD) to {}(USD) per annum.'.format(int(salary*1000)-9000, \
                                                                          int(salary*1000)+9000))