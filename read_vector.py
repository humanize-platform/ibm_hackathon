from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ibm import ChatWatsonx
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

import os

embeddings = WatsonxEmbeddings(
    model_id=EmbeddingTypes.IBM_SLATE_30M_ENG.value,
    url="https://us-south.ml.cloud.ibm.com",
    apikey=os.getenv("WATSONX_APIKEY"),
    project_id=os.getenv("WATSONX_PROJECTKEY"),
)

# Load existing Chroma DB from folder
vectorstore = Chroma(
    collection_name="agentic-rag-chroma",  # Ensure the collection name matches what was used before
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

retriever = vectorstore.as_retriever()

prompt_template = """
        Answer the question based only on the supplied context. If you don't know the answer, say you don't know the answer.
        Context: {context}
        Question: {question}
        Your answer:
        """

prompt = ChatPromptTemplate.from_template(prompt_template)

parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

model = ChatWatsonx(
    model_id="mistralai/mistral-large",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=os.getenv("WATSONX_PROJECTKEY"),
    params=parameters,
)


def getDataFromChroma(question: str):
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain.invoke(question)


print(
    getDataFromChroma(
        "How many people still lack access to safely managed drinking water services as per WHO/UNICEF?"
    )
)
print("*************")
print(getDataFromChroma("List down the Water-related challenges as mentioned by UN"))
print("*************")
print(
    getDataFromChroma(
        "How many people do not have access to basic sanitation facilities such as toilets or latrines?"
    )
)
print("*************")
print(getDataFromChroma("What are the Key messages for World Water Day 2025?"))
print("*************")
print(getDataFromChroma("What is the cryosphere?"))
print("*************")
