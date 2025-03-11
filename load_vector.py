from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

# URLs to fetch
urls = [
    "https://www.un.org/en/global-issues/water",
    "https://www.who.int/news-room/fact-sheets/detail/drinking-water",
    "https://www.unicef.org/wash/water",
    "https://www.who.int/health-topics/water-sanitation-and-hygiene-wash#tab=tab_1",
    "https://www.un.org/en/observances/water-day",
]

# PDFs to process (Update this list with actual file paths)
pdf_files = [
    "./docs/SDG-6-Summary-Progress-Update-2021_Version-July-2021a.pdf",
    "./docs/WGIIAR5-Chap3_FINAL.pdf",
]

# Load documents from URLs
docs = [WebBaseLoader(url).load() for url in urls]

docs_list = [item for sublist in docs for item in sublist]

# Load documents from PDFs
for pdf in pdf_files:
    if os.path.exists(pdf):  # Ensure file exists before loading
        pdf_loader = PyPDFLoader(pdf)
        docs_list.extend(pdf_loader.load())
    else:
        print(f"Warning: PDF file not found - {pdf}")

# Split documents
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=256, chunk_overlap=64
)
doc_splits = text_splitter.split_documents(docs_list)

# Initialize Watsonx embeddings
embeddings = WatsonxEmbeddings(
    model_id=EmbeddingTypes.IBM_SLATE_30M_ENG.value,
    url="https://us-south.ml.cloud.ibm.com",
    apikey=os.getenv("WATSONX_APIKEY"),
    project_id=os.getenv("WATSONX_PROJECTKEY"),
)

# Store in Chroma
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="agentic-rag-chroma",
    embedding=embeddings,
    persist_directory="./chroma_db",
)

print("Chroma vector store updated with URLs and PDFs!")
