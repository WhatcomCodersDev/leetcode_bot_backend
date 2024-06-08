import torch
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel, RobertaTokenizer, RobertaModel
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from scipy.spatial import ConvexHull

import matplotlib.pyplot as plt
import seaborn as sns


class TextEmbedder:
    def __init__(self, model_name="microsoft/codebert-base"):
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)

    def get_text_embedding(self, text_list):
        embeddings = []
        for text in text_list:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
            outputs = self.model(**inputs)
            embeddings.append(outputs.last_hidden_state.mean(dim=1).detach().numpy())
        return np.array(embeddings).squeeze()


class DataPreprocessor:
    def __init__(self, categorical_columns, numerical_columns):
        self.categorical_columns = categorical_columns
        self.numerical_columns = numerical_columns
        self.encoder = OneHotEncoder(sparse_output=False)
        self.scaler = StandardScaler()

    def fit_transform(self, df):
        df_categorical = df[self.categorical_columns].fillna('')
        df_numerical = df[self.numerical_columns].fillna(0)

        categorical_embeddings = self.encoder.fit_transform(df_categorical)
        numerical_embeddings = self.scaler.fit_transform(df_numerical)

        return categorical_embeddings, numerical_embeddings

    def transform(self, df):
        df_categorical = df[self.categorical_columns].fillna('')
        df_numerical = df[self.numerical_columns].fillna(0)

        categorical_embeddings = self.encoder.transform(df_categorical)
        numerical_embeddings = self.scaler.transform(df_numerical)

        return categorical_embeddings, numerical_embeddings

class EmbeddingCombiner:
    def combine_embeddings(self, text_embeddings, categorical_embeddings, numerical_embeddings):
        # return numerical_embeddings
        return np.concatenate([text_embeddings, numerical_embeddings], axis=1)

def convert_to_number(value):
    print(value)
    if ',' in value:
        value = value.replace(',', '.')
    
    if 'M' in value:
        return float(value.replace('M', '')) * 1_000_000
    elif 'K' in value:
        return float(value.replace('K', '')) * 1_000
    else:
        return float(value)



df = pd.read_csv('new_problem_sheet.csv')
df = df.drop(columns=['B75', 'B50', 'NC.io', 'G75', 'LC', 'SP'])
df = df.dropna(subset=['DESCRIPTIONS', 'PROBLEM'])
df = df.dropna(subset=['Accepted', 'Submissions', 'Acceptance Rate', 'Discussion Count'])
df['Accepted'] = df['Accepted'].apply(convert_to_number)
df['Submissions'] = df['Submissions'].apply(convert_to_number)
df['Acceptance Rate'] = df['Acceptance Rate'].apply(lambda x: float(x.replace('%', '')))
df = df[df['TAG'].str.contains("Graph")]
# Define columns
categorical_columns = ['PROBLEM_DIFFICULTY', 'TAG']
numerical_columns = ['Accepted', 'Submissions', 'Acceptance Rate', 'Discussion Count']

# Text embedding
text_embedder = TextEmbedder()
text_embeddings = text_embedder.get_text_embedding((df['DESCRIPTIONS'] + df['PROBLEM']).dropna().to_list())

# Data preprocessing
data_preprocessor = DataPreprocessor(categorical_columns, numerical_columns)
categorical_embeddings, numerical_embeddings = data_preprocessor.fit_transform(df)

# Combine embeddings
embedding_combiner = EmbeddingCombiner()
combined_embeddings = embedding_combiner.combine_embeddings(text_embeddings, categorical_embeddings, numerical_embeddings)


# df_text = df[['PROBLEM', 'DESCRIPTIONS', 'LEVEL', 'TAG']]
# df_categorical = df[['ID', 'LEVEL', 'TAG']]
# df_numerical = df[['Accepted', 'Submissions', 'Acceptance Rate ', 'Discussion Count']]
problem_ids = df['ID']

# unique_tags = df['TAG'].unique()
# unique_levels = df['LEVEL'].unique()

# print(df.head())
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

# def get_text_embedding(text):
#     inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
#     outputs = model(**inputs)
#     return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# df_text = df['DESCRIPTIONS'] + df['PROBLEM']
# df_text = df_text.dropna().to_list()
# print(np.shape(df_text))
# text_embedding = get_text_embedding(df_text)
# print(np.shape(text_embedding))





# Perform clustering
kmeans = KMeans(n_clusters=3, random_state=0)
clusters = kmeans.fit_predict(combined_embeddings)

# df['Cluster'] = clusters

# Reduce dimensionality using PCA
pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(combined_embeddings)

print(f"Shape of reduced embeddings: {reduced_embeddings.shape}")

# Plot the clusters
plt.figure(figsize=(12, 8))
sns.scatterplot(x=reduced_embeddings[:, 0], y=reduced_embeddings[:, 1], hue=clusters, palette='viridis', s=100)
plt.title('Clusters of LeetCode Problems')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend(title='Cluster')

# Annotate each point with the problem ID
# for i, problem_id in enumerate(problem_ids):
#     plt.annotate(problem_id, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=8, alpha=0.75)

for i, name in enumerate(df['PROBLEM']):
    plt.annotate(name, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=8, alpha=0.75)

 # Draw convex hulls around each cluster
    for cluster in np.unique(clusters):
        points = reduced_embeddings[clusters == cluster]
        hull = ConvexHull(points)
        for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], 'r-', lw=2)

plt.show()
