from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv
from cloudant_search import search_cloudant
import json
from langchain.schema import Document

load_dotenv()

query = {"timestamp": {"$gt": "2025-03-10"}}

results = search_cloudant(query)
with open("cloudant_query.json", "w") as file:
    json.dump(results, file, indent=4)