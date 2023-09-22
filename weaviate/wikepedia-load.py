import weaviate

# Instantiate the client with the auth config
client = weaviate.Client(
    url="http://localhost:8080",  # Replace w/ your endpoint
#    auth_client_secret=weaviate.AuthApiKey(api_key="YOUR-WEAVIATE-API-KEY"),  # Replace w/ your Weaviate instance API key
    additional_headers={
        "X-OpenAI-Api-Key": "OPEN-API-KEY",
    },
)

client.schema.delete_all()  # ⚠️ uncomment to start from scratch by deleting ALL data

# ===== Create Article class for the schema =====
article_class = {
    "class": "Article",
    "description": "An article from the Simple English Wikipedia data set",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        # Match how OpenAI created the embeddings for the `content` (`text`) field
        "text2vec-openai": {
            "model": "ada",
            "modelVersion": "002",
            "type": "text",
            "vectorizeClassName": False
        }
    },
    "properties": [
        {
            "name": "title",
            "description": "The title of the article",
            "dataType": ["text"],
            # Don't vectorize the title
            "moduleConfig": {"text2vec-openai": {"skip": True}}
        },
        {
            "name": "content",
            "description": "The content of the article",
            "dataType": ["text"],
        }
    ]
}

# Add the Article class to the schema
client.schema.create_class(article_class)
print('Created schema');

# ===== Import data =====
# Settings for displaying the import progress
counter = 0
interval = 100  # print progress every this many records

# Create a pandas dataframe iterator with lazy-loading,
# so we don't load all records in RAM at once.
import pandas as pd
csv_iterator = pd.read_csv(
    'vector_database_wikipedia_articles_embedded.csv',
    usecols=['id', 'url', 'title', 'text', 'content_vector'],
    chunksize=100,  # number of rows per chunk
    # nrows=350  # optionally limit the number of rows to import
)

# Iterate through the dataframe chunks and add each CSV record to the batch
import ast
client.batch.configure(batch_size=100)  # Configure batch
with client.batch as batch:
  for chunk in csv_iterator:
      for index, row in chunk.iterrows():

          properties = {
              "title": row.title,
              "content": row.text,
              "url": row.url
          }

          # Convert the vector from CSV string back to array of floats
          vector = ast.literal_eval(row.content_vector)

          # Add the object to the batch, and set its vector embedding
          batch.add_data_object(properties, "Article", vector=vector)

          # Calculate and display progress
          counter += 1
          if counter % interval == 0:
              print(f"Imported {counter} articles...")
print(f"Finished importing {counter} articles.")
