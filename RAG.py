
import os
import json

from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document # for including metadata filter and for json splitter *** ?
from langchain_community.retrievers import BM25Retriever # for lexical msearch
from langchain_classic.retrievers import EnsembleRetriever # reciprocal rank fusion for both lexical search and semantic search :)



load_dotenv()
secret_key = os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key=secret_key)

PERSIST_DIR = "./chrome_db"

# load text gotten from image folder
# This is heavily customed. 
with open('main_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)






# note, chunk is relative to existing json file. Tweak where necessary
def chunk_and_embed(doc, embed_model):

    chunks = []
    for page_no, (question, answer) in enumerate(doc.items()):
        page_content= f'Question{question}: \n Context&Answer {answer}'
        meta_data = {'page_number': page_no+1}
        my_doc = Document(page_content = page_content, metadata= meta_data)
        chunks.append(my_doc)
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150).. previous chunking strategy used
    #chunks = text_splitter.split_text(doc) 
    embedding_model = embed_model
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR): # to prevent any further embedding again and save tokens.
        print('Retrieving from Vector Database.....)')
        # 1. loads the persists vector db. no api call is made. it is written solely when an input is being done the embed model can match the input to the necessary vector database
        vector_database = Chroma(embedding_function=embed_model, persist_directory=PERSIST_DIR)
        # if you notice very well, the if doesn't use the chunk it

    else:
        print('Chunking the data.....)')
        vector_database = Chroma.from_documents(chunks, embedding_model, persist_directory=PERSIST_DIR)

    vector_retriever = vector_database.as_retriever(search_kwargs = {"k": 3}) # retrieve the relevant chunks (how does this now match the input query)
    lexical_retrieval = BM25Retriever.from_documents(chunks)
    lexical_retrieval.k = 3

    hybrid_retrieval = EnsembleRetriever(retrievers = [vector_retriever, lexical_retrieval], weights = [0.5, 0.5])
    return hybrid_retrieval

embed_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=secret_key)

final_retrieval = chunk_and_embed(data, embed_model)
#final_retrieval = chunk_and_embed(full_document,embed_model)

def retrieve_and_reason(query, retrieve):

    docs = retrieve.invoke(query) # get the relevant document # this is were the similarity matches happens # semantic search is here !!!!
    #print(docs)
    context = "\n\n".join([d.page_content for d in docs])
    sources = ", ".join([f'Page {s.metadata.get("page_number")}' for s in docs])

    # THE PROMPT
    prompt = f"""
    Context information is below.
    ---------------------
    {context}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {query}
    Answer:
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    #print(prompt)
    final_answer = f"{response.choices[0].message.content} \n\n\n Gotten from {sources}"
    return final_answer


#print(retrieve_and_reason(input(str('Input Prompt: ')),final_retrieval))


# CONVERT TO OOP !!
# tell me the role of a data scientist