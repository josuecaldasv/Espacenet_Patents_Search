import pandas as pd
import os
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from sklearn.manifold import TSNE
import seaborn as sns
import umap.umap_ as umap
from matplotlib.offsetbox import AnchoredText
import gensim
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
import pyLDAvis
import pyLDAvis.lda_model
import pickle

import utils

# 1. Load data
# ------------

input_path = '../extraction/biblio_output/'
output_path = 'lda/'
os.makedirs(output_path, exist_ok=True)

patents = utils.get_patents_citations(input_path)
abstract_dict = {patent['patent_number']: patent.get('abstract', 'Unavailable information') for patent in patents}
df = pd.DataFrame(list(abstract_dict.items()), columns=['PatentID', 'Abstract'])

# 2. Preprocess data
# ------------------


df['Cleaned_Abstract'] = df['Abstract'].apply(utils.clean_text)

# 3. Vectorize data
# -----------------

vectorizer = CountVectorizer(max_features=2000, min_df=5, max_df=0.85)
tfidf_matrix = vectorizer.fit_transform(df['Cleaned_Abstract'])
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

# 4. Fit LDA model
# ----------------

n_topics = 4
lda = LatentDirichletAllocation(n_components=n_topics, max_iter=20, learning_decay=0.7, random_state=42)
lda.fit(tfidf_matrix)
terms = vectorizer.get_feature_names_out()

with open (os.path.join(output_path, 'lda_topics.txt'), 'w') as f:
    for idx, topic in enumerate(lda.components_):
        f.write(f'Topic {idx + 1}:\n')
        f.write(str([terms[i] for i in topic.argsort()[-10:]]) + '\n')


# 5. Plot the number of abstracts per topic
# -----------------------------------------

topic_assignments = lda.transform(tfidf_matrix).argmax(axis=1)
df['Topic'] = topic_assignments
topic_counts = df['Topic'].value_counts()
plt.figure(figsize=(10, 6))
plt.bar(topic_counts.index, topic_counts.values, color='skyblue', edgecolor='black')
plt.title('Number of Patents by Topic', fontsize=16, fontweight='bold')
plt.xlabel('Topic', fontsize=14)
plt.ylabel('Number of Patents', fontsize=14)
xtick_labels = [f'Topic {int(i) + 1}' for i in topic_counts.index]
plt.xticks(topic_counts.index, xtick_labels, fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'abstracts_per_topic.png'), dpi=300)


# 6. Word cloud for each topic
# -----------------------------

for idx, topic in enumerate(lda.components_):
    topic_words = [terms[i] for i in topic.argsort()[-30:]]
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(topic_words))
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f'wordcloud_topic_{idx + 1}.png'), dpi=300)


# 7. Reduce dimensionality with t-SNE
# -----------------------------------

tsne_model = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
tsne_results = tsne_model.fit_transform(lda.transform(tfidf_matrix))
df_tsne = pd.DataFrame(tsne_results, columns=['x', 'y'])
df_tsne['Topic'] = df['Topic']
df_tsne['Topic_label'] = df_tsne['Topic'].apply(lambda x: f'Topic {x+1}')


# 8. Plot t-SNE visualization
# ---------------------------

plt.figure(figsize=(12, 8))
palette = sns.color_palette('hsv', n_topics)
sns.scatterplot(
    x='x', y='y', hue='Topic_label', palette=palette, data=df_tsne, legend='full', alpha=0.7, s=30
)
plt.title('t-SNE visualization of LDA topics', fontsize=16, fontweight='bold')
plt.xlabel('')
plt.ylabel('')
plt.xticks([])
plt.yticks([])
for i in range(n_topics):
    x_mean = df_tsne[df_tsne['Topic'] == i]['x'].mean()
    y_mean = df_tsne[df_tsne['Topic'] == i]['y'].mean()
    plt.text(x_mean, y_mean, f'Topic {i+1}', fontsize=12, fontweight='bold', ha='center', va='center')
plt.legend(title='Topics', bbox_to_anchor=(1.05, 0.5), loc='center left', fontsize=12, title_fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'lda_tsne_plot.png'), dpi=300)


# 9. Reduce dimensionality with UMAP
# ----------------------------------

umap_model = umap.UMAP(n_neighbors=15, n_components=2, random_state=42)
umap_results = umap_model.fit_transform(lda.transform(tfidf_matrix))
df_umap = pd.DataFrame(umap_results, columns=['x', 'y'])
df_umap['Topic'] = df['Topic']
df_umap['Topic_label'] = df_umap['Topic'].apply(lambda x: f'Topic {x+1}')

# 10. Plot UMAP visualization
# ---------------------------

plt.figure(figsize=(12, 8))
sns.scatterplot(
    x='x', y='y', hue='Topic_label', palette=palette, data=df_umap, legend='full', alpha=0.7, s=30
)
plt.title('UMAP visualization of LDA topics', fontsize=16, fontweight='bold')
plt.xlabel('')
plt.ylabel('')
plt.xticks([])
plt.yticks([])
for i in range(n_topics):
    x_mean = df_umap[df_umap['Topic'] == i]['x'].mean()
    y_mean = df_umap[df_umap['Topic'] == i]['y'].mean()
    plt.text(x_mean, y_mean, f'Topic {i+1}', fontsize=12, fontweight='bold', ha='center', va='center')
plt.legend(title='Topics', bbox_to_anchor=(1.05, 0.5), loc='center left', fontsize=12, title_fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'lda_umap_plot.png'), dpi=300)


# 11. Topic Coherence Evaluation
# ------------------------------

# texts = df['Cleaned_Abstract'].apply(lambda x: x.split())
# dictionary = corpora.Dictionary(texts)
# corpus = [dictionary.doc2bow(text) for text in texts]

# n_topics_list = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# coherence_results = []

# for n in n_topics_list:
#     lda = LatentDirichletAllocation(n_components=n, max_iter=20, learning_decay=0.7, random_state=42)
#     lda.fit(tfidf_matrix)
#     lda_gensim = gensim.models.ldamodel.LdaModel(
#         corpus=corpus,
#         id2word=dictionary,
#         num_topics=n,
#         passes=10,
#         random_state=42,
#         alpha='auto'
#     )
#     coherence_model = CoherenceModel(model=lda_gensim, texts=texts, dictionary=dictionary, coherence='c_v')
#     coherence = round(coherence_model.get_coherence(), 4)
#     print(f'Topic {n}: {coherence}')
#     coherence_results.append((n, coherence))
#     with open(os.path.join(output_path, 'coherence_results.txt'), 'a') as f:
#         f.write(f'Topic {n}: {coherence}\n')

# coherence_results = coherence_results[1:]
# coherence_df = pd.DataFrame(coherence_results, columns=['n_topics', 'coherence'])
# plt.figure(figsize=(10, 8))
# ax = sns.barplot(
#     x='n_topics',
#     y='coherence',
#     data=coherence_df,
#     color='orchid'
# )
# for index, value in enumerate(coherence_df['coherence']):
#     ax.text(index, value + 0.005, str(value), ha='center')
# plt.ylim(0.3, 0.5)
# plt.xlabel('Number of Topics')
# plt.ylabel('Coherence Score')
# plt.title('Coherence Score for Different Numbers of Topics')
# plt.xticks(ticks=range(len(coherence_df)), labels=coherence_df['n_topics'])
# plt.tight_layout()
# plt.savefig('lda/coherence_scores.png', dpi=300)


# 12. pyLDAvis visualization
# --------------------------

lda_vis_data = pyLDAvis.lda_model.prepare(lda, tfidf_matrix, vectorizer)
pyLDAvis.save_html(lda_vis_data, os.path.join(output_path, 'lda_vis.html'))
