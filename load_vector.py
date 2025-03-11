from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

urls = ['https://www.un.org/en/global-issues/water',
        'https://www.who.int/news-room/fact-sheets/detail/drinking-water',
        'https://www.unicef.org/wash/water',
        'https://www.who.int/health-topics/water-sanitation-and-hygiene-wash#tab=tab_1',
        'https://www.un.org/en/observances/water-day',
        'https://www.ipcc.ch/report/ar5/wg2/freshwater-resources/'
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=250, chunk_overlap=64)
doc_splits = text_splitter.split_documents(docs_list)

embeddings = WatsonxEmbeddings(
    model_id=EmbeddingTypes.IBM_SLATE_30M_ENG.value,
    url="https://us-south.ml.cloud.ibm.com",
    apikey=os.getenv("WATSONX_APIKEY"),
    project_id=os.getenv("WATSONX_PROJECTKEY"),
)

vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="agentic-rag-chroma",
    embedding=embeddings,
    persist_directory="./chroma_db"
)

