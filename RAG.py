import pytesseract
from PIL import Image, ImageOps
import os
from pillow_heif import register_heif_opener
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document # for including metadata filter 
from langchain_community.retrievers import BM25Retriever # for lexical msearch
from langchain_classic.retrievers import EnsembleRetriever # reciprocal rank fusion for both lexical search and semantic search :)



load_dotenv()
secret_key = os.getenv("open_api_key")
client = OpenAI(api_key=secret_key)

register_heif_opener()

PERSIST_DIR = "./chrome_db"


# Add this line (this is the default path for Apple Silicon Macs like your M-series MacBook Air)
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


def images_list_obj(doc):
    img_list_obj = []
    for i in os.listdir(doc):
        a = os.path.join(doc,i)
        a_obj = Image.open(a)
        img_list_obj.append(a_obj)
    return img_list_obj[0:5]

def extract_text_from_img(text_folder: list) -> list:

    full_text = []
    
    for img in text_folder:
        # Preprocessing: Grayscale improves Tesseract accuracy by up to 50%
        gray_page = ImageOps.grayscale(img)
        
        # Run OCR with Page Segmentation Mode 3 (Fully automatic page segmentation)
        text = pytesseract.image_to_string(gray_page, config='--psm 3')
        full_text.append(text)
        
    return "\n\n".join(full_text)

full_document = extract_text_from_img(images_list_obj(doc=r'/Users/mubaraq/Downloads/Deloitte'))

print((full_document))
print(len(full_document))

def chunk_and_embed(doc, embed_model):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_text(doc)
    embedding_model = embed_model
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR): # to prevent any further embedding again and save tokens.

        # 1. loads the persists vector db. no api call is made. it is written solely when an input is being done the embed model can match the input to the necessary vector database
        vector_database = Chroma(embedding_function=embed_model, persist_directory=PERSIST_DIR)
        # if you notice very well, the if doesn't use the chunk it

    else:
        # 1. Chunk the OCR-extracted text
        

        # Here we create the metadata. Let's call it page by page :) ... incoming :)

        # 2. Initialize an embedding model
        embedding_model = embed_model

        # 3. Create the vector database store and save in a persist file
        # You know something interesing in this section that saves/created the vector databse, we can also include/create a meta data from it because currently it doesn't store any meta data (metadata is zero)
        vector_database = Chroma.from_texts(chunks, embedding_model, persist_directory=PERSIST_DIR)

    vector_retriever = vector_database.as_retriever(search_kwargs = {"k": 3}) # retrieve the relevant chunks (how does this now match the input query)
    lexical_retrieval = BM25Retriever.from_texts(chunks)
    lexical_retrieval.k = 3

    hybrid_retrieval = EnsembleRetriever(retrievers = [vector_retriever, lexical_retrieval], weights = [0.5, 0.5])
    return hybrid_retrieval

embed_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=secret_key)
chunk_and_embed(full_document,embed_model)



def retrieve_and_reason(query):
# Retrieve the closest text chunks matching the query

    docs = chunk_and_embed(full_document, embed_model).invoke(query) # get the relevant document # this is were the similarity matches happens # semantic search is here !!!!
    context = "n\n".join([d.page_content for d in docs])

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

    return response.choices[0].message.content

print(retrieve_and_reason(input(str('Input Prompt: '))))



#if __name__ = '__main__':

