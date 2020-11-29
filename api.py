from flask import Flask, request
from flask_restful import Api, Resource
from tensorflow import keras

app = Flask(__name__)
api = Api(app)

def similarity(sentences, query):
    from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer('xlm-r-100langs-bert-base-nli-mean-tokens')
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    sentence_embeddings = model.encode(sentences)
    # print('Sample BERT embedding vector - length', len(sentence_embeddings[0]))
    import scipy
    queries = [query]
    query_embeddings = model.encode(queries)

    # Find the closest 3 sentences of the corpus for each query sentence based on cosine similarity
    number_top_matches = 5 #@param {type: "number"}
    # print("Semantic Search Results")
    sucess = []
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], sentence_embeddings, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        print("\n\n======================\n\n")
        print("Query:", query)
        print("\nTop 5 most similar sentences in corpus:")

        for idx, distance in results[0:number_top_matches]:
            print(sentences[idx].strip(), "(Cosine Score: %.4f)" % (1-distance))
            sucess.append(sentences[idx].strip())
    return sucess

@app.route('/', methods=['POST'])
def test():
    input_json = request.get_json(force=True)
    # print("TEST", input_json)
    query = input_json["query"]
    sents = input_json["data"]
        
    import time
    start = time.time()
    results = similarity(sents, query)
    if len(results) < 4:
        statusCode = "404 Not Found!"
    else:
        statusCode = "200 Success!"

    print("Total time: ", time.time() - start)
    return {"statusCode": statusCode,
            "query": query,
            "result": results,
            }

if __name__ == "__main__":
    app.run(port=12345 ,debug=True)