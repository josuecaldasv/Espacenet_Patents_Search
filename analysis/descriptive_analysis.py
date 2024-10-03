import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager

import utils

font_path = 'rankings/plots/SimHei.ttf'
prop = font_manager.FontProperties(fname=font_path)


patents_info = pd.read_excel('graphs/total_patents_df.xlsx')
patents_info = patents_info.drop(columns=['Unnamed: 0'])


# 1. MOST CITED PATENTS
# ======================

patents_most_cited = patents_info.sort_values(by='input_degree', ascending=False)

## 1.1. Countries with most cited patents
# ----------------------------------------

patents_most_cited_countries = patents_most_cited.copy()
patents_most_cited_countries['country'] = patents_most_cited_countries.apply(utils.fill_country_from_patent_number, axis=1)
countries_data = patents_most_cited_countries.explode('country')
countries_citations = countries_data.groupby('country').agg({'input_degree': 'sum'}).reset_index()
top_countries = countries_citations.sort_values(by='input_degree', ascending=False).head(25)
top_countries_dict = top_countries.to_dict(orient='records')
with open ('rankings/top_countries_cited.json', 'w') as f:
    json.dump(top_countries_dict, f, indent=4)

top_countries_plot = top_countries.head(10)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='country',
    x='input_degree',
    data=top_countries_plot,
    color='skyblue'
)
for index, value in enumerate(top_countries_plot['input_degree']):
    ax.text(value + 5, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Country')
plt.title('Top Cited Countries in Patents')
plt.yticks(ticks=range(len(top_countries_plot)), labels=top_countries_plot['country'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_countries_cited.png', dpi=300)

## 1.2. Inventors with most cited patents
# ----------------------------------------

patents_most_cited_inventors = patents_most_cited.copy()
patents_most_cited_inventors['inventor_names'] = patents_most_cited['inventor_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_most_cited_inventors.explode('inventor_names')
df_exploded = df_exploded.assign(inventor_names=df_exploded['inventor_names'].str.split(',')).explode('inventor_names')
df_exploded['inventor_names'] = df_exploded['inventor_names'].str.strip()
df_exploded = df_exploded[df_exploded['inventor_names'] != 'Unavailable information']
inventor_citations = df_exploded.groupby('inventor_names')['input_degree'].sum()
top_inventors = inventor_citations.sort_values(ascending=False).head(20)
top_inventors_dict = top_inventors.to_dict()
with open ('rankings/top_inventors_cited.json', 'w') as f:
    json.dump(top_inventors_dict, f, indent=4)

top_inventors_plot = top_inventors.head(10).reset_index() 
top_inventors_plot['inventor_names'] = top_inventors_plot['inventor_names'].apply(utils.normalize_text)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='inventor_names',
    x='input_degree',
    data=top_inventors_plot,
    color='indianred'
)
for index, value in enumerate(top_inventors_plot['input_degree']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Inventor')
plt.title('Top Cited Inventors in Patents')
plt.yticks(ticks=range(len(top_inventors_plot)), labels=top_inventors_plot['inventor_names'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_inventors_cited.png', dpi=300)

## 1.3. Applicants with most cited patents
# ----------------------------------------

patents_most_cited_applicants = patents_most_cited.copy()
patents_most_cited_applicants['applicant_names'] = patents_most_cited['applicant_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_most_cited_applicants.explode('applicant_names')
df_exploded = df_exploded.assign(applicant_names=df_exploded['applicant_names'].str.split(',')).explode('applicant_names')
df_exploded['applicant_names'] = df_exploded['applicant_names'].str.strip()
df_exploded = df_exploded[df_exploded['applicant_names'] != 'Unavailable information']
applicant_citations = df_exploded.groupby('applicant_names')['input_degree'].sum()
top_applicants = applicant_citations.sort_values(ascending=False).head(20)
top_applicants_dict = top_applicants.to_dict()
with open ('rankings/top_applicants_cited.json', 'w') as f:
    json.dump(top_applicants_dict, f, indent=4)

top_applicants_plot = top_applicants.head(10).reset_index()
top_applicants_plot['applicant_names'] = top_applicants_plot['applicant_names'].apply(utils.normalize_text)
top_applicants_plot.iloc[1, 0] = 'The United States Department of Energy'
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='applicant_names',
    x='input_degree',
    data=top_applicants_plot,
    color='lightgreen'
)
for index, value in enumerate(top_applicants_plot['input_degree']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Applicant')
plt.title('Top Cited Applicants in Patents')
plt.yticks(ticks=range(len(top_applicants_plot)), labels=top_applicants_plot['applicant_names'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_applicants_cited.png', dpi=300)


# 1.4. Most cited patents
# ------------------------

top_patents = patents_most_cited.head(10)
top_patents['inventor_names'] = top_patents['inventor_names'].apply(utils.clean_and_deduplicate_names)
top_patents['applicant_names'] = top_patents['applicant_names'].apply(utils.clean_and_deduplicate_names)
top_patents_dict = top_patents.to_dict(orient='records')
with open ('rankings/top_patents_cited.json', 'w') as f:
    json.dump(top_patents_dict, f, indent=4, ensure_ascii=False)

top_patents_plot = top_patents.reset_index()
top_patents_plot = top_patents_plot.drop(columns=['index', 'abstract', 'year', 'inventor_names', 'applicant_names',
                                                  'country', 'patent_number', 'output_degree', 'pagerank'])
top_patents_plot.iloc[6, 0] = 'A process for preparing lithium aluminum hydride-aluminum hydride complexes'
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='invention_title',
    x='input_degree',
    data=top_patents_plot,
    color='steelblue'
)
for index, value in enumerate(top_patents_plot['input_degree']):
    ax.text(value + 0.20, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Patent')
plt.title('Top Cited Patents')
plt.yticks(ticks=range(len(top_patents_plot)), labels=top_patents_plot['invention_title'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_patents_cited.png', dpi=300)


# 2. MOST CITING PATENTS
# =======================

patents_most_citing = patents_info.sort_values(by='output_degree', ascending=False)

# 2.1. Countries with most citing patents
# ----------------------------------------

patents_most_citing = patents_most_citing.copy()
patents_most_citing['country'] = patents_most_citing.apply(utils.fill_country_from_patent_number, axis=1)
countries_data = patents_most_citing.explode('country')
countries_citations = countries_data.groupby('country').agg({'output_degree': 'sum'}).reset_index()
top_countries = countries_citations.sort_values(by='output_degree', ascending=False).head(25)
top_countries_dict = top_countries.to_dict(orient='records')
with open ('rankings/top_countries_citing.json', 'w') as f:
    json.dump(top_countries_dict, f, indent=4)

top_countries_plot = top_countries.head(10)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='country',
    x='output_degree',
    data=top_countries_plot,
    color='skyblue'
)
for index, value in enumerate(top_countries_plot['output_degree']):
    ax.text(value + 5, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Country')
plt.title('Top Citing Countries in Patents')
plt.yticks(ticks=range(len(top_countries_plot)), labels=top_countries_plot['country'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_countries_citing.png', dpi=300)


# 2.2. Inventors with most citing patents
# ----------------------------------------

patents_most_citing_inventors = patents_most_citing.copy()
patents_most_citing_inventors['inventor_names'] = patents_most_citing_inventors['inventor_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_most_citing_inventors.explode('inventor_names')
df_exploded = df_exploded.assign(inventor_names=df_exploded['inventor_names'].str.split(',')).explode('inventor_names')
df_exploded['inventor_names'] = df_exploded['inventor_names'].str.strip()
df_exploded = df_exploded[df_exploded['inventor_names'] != 'Unavailable information']
inventor_citations = df_exploded.groupby('inventor_names')['output_degree'].sum()
top_inventors = inventor_citations.sort_values(ascending=False).head(20)
top_inventors_dict = top_inventors.to_dict()
with open ('rankings/top_inventors_citing.json', 'w') as f:
    json.dump(top_inventors_dict, f, indent=4, ensure_ascii=False)

top_inventors_plot = top_inventors.head(10).reset_index()
top_inventors_plot['inventor_names'] = top_inventors_plot['inventor_names'].apply(utils.normalize_text)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='inventor_names',
    x='output_degree',
    data=top_inventors_plot,
    color='indianred'
)
for index, value in enumerate(top_inventors_plot['output_degree']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Inventor')
plt.title('Top Citing Inventors in Patents')
plt.yticks(ticks=range(len(top_inventors_plot)), labels=top_inventors_plot['inventor_names'], wrap=True, fontproperties=prop)
plt.tight_layout()
plt.savefig('rankings/plots/top_inventors_citing.png', dpi=300)

# 2.3. Applicants with most citing patents
# ----------------------------------------

patents_most_citing_applicants = patents_most_citing.copy()
patents_most_citing_applicants['applicant_names'] = patents_most_citing_applicants['applicant_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_most_citing_applicants.explode('applicant_names')
df_exploded = df_exploded.assign(applicant_names=df_exploded['applicant_names'].str.split(',')).explode('applicant_names')  
df_exploded['applicant_names'] = df_exploded['applicant_names'].str.strip()
df_exploded = df_exploded[df_exploded['applicant_names'] != 'Unavailable information']
applicant_citations = df_exploded.groupby('applicant_names')['output_degree'].sum()
top_applicants = applicant_citations.sort_values(ascending=False).head(20)
top_applicants_dict = top_applicants.to_dict()
with open ('rankings/top_applicants_citing.json', 'w') as f:
    json.dump(top_applicants_dict, f, indent=4, ensure_ascii=False)

top_applicants_plot = top_applicants.head(10).reset_index()
top_applicants_plot['applicant_names'] = top_applicants_plot['applicant_names'].apply(utils.normalize_text)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='applicant_names',
    x='output_degree',
    data=top_applicants_plot,
    color='lightgreen'
)
for index, value in enumerate(top_applicants_plot['output_degree']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Citations')
plt.ylabel('Applicant')
plt.title('Top Citing Applicants in Patents')
plt.yticks(ticks=range(len(top_applicants_plot)), labels=top_applicants_plot['applicant_names'], wrap=True, fontproperties=prop)
plt.tight_layout()
plt.savefig('rankings/plots/top_applicants_citing.png', dpi=300)


# 3. MOST NUMEROUS PATENTS PRESENTED
# ==================================

patents_most_numerous = patents_info.sort_values(by='input_degree', ascending=False)

# 3.1. Countries with most patents presented
# ------------------------------------------

patents_most_numerous_countries = patents_most_numerous.copy()
patents_most_numerous_countries['country'] = patents_most_numerous_countries.apply(utils.fill_country_from_patent_number, axis=1)
countries_data = patents_most_numerous_countries.explode('country')
countries_data_count = countries_data['country'].value_counts().reset_index()
countries_data_count.columns = ['country', 'count']
top_countries = countries_data_count.head(25)
top_countries_dict = top_countries.to_dict(orient='records')
with open('rankings/top_countries_presented.json', 'w') as f:
    json.dump(top_countries_dict, f, indent=4)
top_countries_plot = top_countries.head(10).reset_index(drop=True)
top_countries_plot['country'] = top_countries_plot['country'].astype(str).str.strip()
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='country',
    x='count',
    data=top_countries_plot,
    color='skyblue'
)
for index, value in enumerate(top_countries_plot['count']):
    ax.text(value + 5, index, str(value), va='center')
plt.xlabel('Number of Patents')
plt.ylabel('Country')
plt.title('Top Countries Presenting Patents')
plt.yticks(ticks=range(len(top_countries_plot)), labels=top_countries_plot['country'], wrap=True)
plt.tight_layout()
plt.savefig('rankings/plots/top_countries_presented.png', dpi=300)

# 3.2. Inventors with most patents presented
# ------------------------------------------

patents_inventors = patents_most_cited.copy()
patents_inventors['inventor_names'] = patents_inventors['inventor_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_inventors.explode('inventor_names')
df_exploded = df_exploded.assign(inventor_names=df_exploded['inventor_names'].str.split(',')).explode('inventor_names')
df_exploded['inventor_names'] = df_exploded['inventor_names'].str.strip()
inventor_patent_count = df_exploded['inventor_names'].value_counts().reset_index()
inventor_patent_count.columns = ['inventor_names', 'patent_count']
inventor_patent_count = inventor_patent_count[inventor_patent_count['inventor_names'] != 'Unavailable information']
top_inventors = inventor_patent_count.head(20)
top_inventors_dict = top_inventors.to_dict(orient='records')
with open('rankings/top_inventors_presented.json', 'w') as f:
    json.dump(top_inventors_dict, f, indent=4, ensure_ascii=False)

top_inventors_plot = top_inventors.head(10)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='inventor_names',
    x='patent_count',
    data=top_inventors_plot,
    color='indianred'
)
for index, value in enumerate(top_inventors_plot['patent_count']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Patents')
plt.ylabel('Inventor')
plt.title('Top Inventors Presenting Patents')
plt.yticks(ticks=range(len(top_inventors_plot)), labels=top_inventors_plot['inventor_names'], wrap=True, fontproperties=prop)
plt.tight_layout()
plt.savefig('rankings/plots/top_inventors_presented.png', dpi=300)

# 3.3. Applicants with most patents presented
# -------------------------------------------

patents_applicants = patents_most_cited.copy()
patents_applicants['applicant_names'] = patents_applicants['applicant_names'].apply(utils.clean_and_deduplicate_names)
df_exploded = patents_applicants.explode('applicant_names')
df_exploded = df_exploded.assign(applicant_names=df_exploded['applicant_names'].str.split(',')).explode('applicant_names')
df_exploded['applicant_names'] = df_exploded['applicant_names'].str.strip()
applicant_patent_count = df_exploded['applicant_names'].value_counts().reset_index()
applicant_patent_count.columns = ['applicant_names', 'patent_count']
applicant_patent_count = applicant_patent_count[applicant_patent_count['applicant_names'] != 'Unavailable information']
top_applicants = applicant_patent_count.head(20)
top_applicants_dict = top_applicants.to_dict(orient='records')
with open('rankings/top_applicants_presented.json', 'w') as f:
    json.dump(top_applicants_dict, f, indent=4, ensure_ascii=False)

top_applicants_plot = top_applicants.head(10)
plt.figure(figsize=(10, 8))
ax = sns.barplot(
    y='applicant_names',
    x='patent_count',
    data=top_applicants_plot,
    color='lightgreen'
)
for index, value in enumerate(top_applicants_plot['patent_count']):
    ax.text(value + 0.35, index, str(value), va='center')
plt.xlabel('Number of Patents')
plt.ylabel('Applicant')
plt.title('Top Applicants Presenting Patents')
plt.yticks(ticks=range(len(top_applicants_plot)), labels=top_applicants_plot['applicant_names'], wrap=True, fontproperties=prop)
plt.tight_layout()
plt.savefig('rankings/plots/top_applicants_presented.png', dpi=300)
