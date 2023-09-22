import csv
import json
import random
import openai
import time
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

# Extract the book titles
def csv_load(file):
    with open(file, newline='') as f:
        reader=csv.reader(f, delimiter=',')
        for row in reader:
            yield row[1]

# Searching book titles
# Define parameters
FILE = '/Users/mangat.rai/datastax/zilliz/books.csv'  # Download it from https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks and save it in the folder that holds your script.
COLLECTION_NAME = 'title_db'  # Collection name
DIMENSION = 1536  # Embeddings size
COUNT = 210  # How many titles to embed and insert
URI = 'https://in03-a33c2f70e909d9a.api.gcp-us-west1.zillizcloud.com'  # Endpoint URI obtained from Zilliz Cloud
USER = 'mangatrai@duck.com'  # Username specified when you created this cluster
PASSWORD='jwj3dzr2qge6cjq*YRZ'  # Password set for that account
OPENAI_ENGINE = 'text-embedding-ada-002'  # Which engine to use
openai.api_key = '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'  # Use your own Open AI API Key here
zilliz_api_key = 'fd3cf5462d31b7e4ede7344beaeec7c1a76ee4027064b8ee8a3084916cb9d5e35edd99e654a8f254fc3bae13b9d1208b1dec4d85' # Use your own Zilliz Cloud API key here

# For serverless cluster
TOKEN = zilliz_api_key

# For dedicated cluster
# TOKEN = f"{USER}:{PASSWORD}"

# Connect to Zilliz Cloud
connections.connect(uri=URI, token=TOKEN, secure=True)

# Remove collection if it already exists
if utility.has_collection(COLLECTION_NAME):
    utility.drop_collection(COLLECTION_NAME)

# Create collection which includes the id, title, and embedding.
fields = [
    FieldSchema(name='id', dtype=DataType.INT64, descrition='Ids', is_primary=True, auto_id=False),
    FieldSchema(name='title', dtype=DataType.VARCHAR, description='Title texts', max_length=200),
    FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, description='Embedding vectors', dim=DIMENSION)
]
schema = CollectionSchema(fields=fields, description='Title collection')
collection = Collection(name=COLLECTION_NAME, schema=schema)

# Create an index for the collection.
index_params = {
    'index_type': 'AUTOINDEX',
    'metric_type': 'L2',
    'params': {}
}
collection.create_index(field_name="embedding", index_params=index_params)

# Extract embedding from text using OpenAI
def embed(text):
    return openai.Embedding.create(
        input=text,
        engine=OPENAI_ENGINE)["data"][0]["embedding"]

# Insert each title and its embedding
for idx, text in enumerate(random.sample(sorted(csv_load(FILE)), k=COUNT)):  # Load COUNT amount of random values from dataset
    ins=[[idx], [(text[:198] + '..') if len(text) > 200 else text], [embed(text)]]  # Insert the title id, the title text, and the title embedding vector
    collection.insert(ins)
    time.sleep(1)  # Free OpenAI account limited to 60 RPM
