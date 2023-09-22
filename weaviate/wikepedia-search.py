import weaviate
import json

# Instantiate the client with the auth config
client = weaviate.Client(
    url="http://localhost:8080",  # Replace w/ your endpoint
#    auth_client_secret=weaviate.AuthApiKey(api_key="YOUR-WEAVIATE-API-KEY"),  # Replace w/ your Weaviate instance API key
    additional_headers={
        "X-OpenAI-Api-Key": "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",
    },
)

nearText = {"concepts": ["modern art in Europe"]}

print("\n****** nearText Search Results *******\n")

result = (
    client.query
    .get("Article", ["title", "content"])
    .with_near_text(nearText)
    .with_limit(1)
    .do()
)

print(json.dumps(result, indent=4))

print("\n****** HYBRID SEARCH NEXT *******\n")
# hybrid

result = (
    client.query
    .get("Article", ["title", "content"])
    .with_hybrid("jackfruit", alpha=0.5)  # default 0.75
    .with_limit(3)
    .do()
)

print(json.dumps(result, indent=4))
