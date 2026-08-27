# building the flask app

from RAG import data, chunk_and_embed, retrieve_and_reason, embed_model
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

final_retrieval = chunk_and_embed(data, embed_model)

@app.route('/api/rag', methods=['POST'])
def rag_query():
    data_request = request.get_json()

    if not data_request: 
        return jsonify({'Error' : 'Missing data'}, 400)

    user_input = data_request['query']

    try:
        chat_response = retrieve_and_reason(user_input, final_retrieval)

        return jsonify({
            'status':'sucess',
            'message':chat_response
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message':e}), 500


if __name__ == '__main__':

    app.run(host = '0.0.0.0', port = 4001, debug = True)


# You can opt in to test using postman :)


# Continuously chat system flow 
# OOP format
# Connect to a front end

# CI/CD
# since you've containerised ---> deploy to AWS
# Add an MCP

'''


'''
