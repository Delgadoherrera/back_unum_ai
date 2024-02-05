#vectors_chains

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import openai
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import json
import requests
import os

def send_to_gpt(question, extracted_text):
    print('SENDING DATA TO GPT', extracted_text)
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    # Configurar el cuerpo de la solicitud para la API de chat
    payload = {
        "model": "gpt-3.5-turbo-16k",  # El modelo de chat
        "messages": [
            {"role": "user", "content": question},
            {"role": "user", "content": extracted_text}
        ],
        "max_tokens": 1500
    }

    # Enviar la solicitud a la API de chat de OpenAI
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        # Procesar la respuesta
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    else:
        # Manejar errores
        return f"Error en la solicitud: {response.status_code}, {response.text}"


def create_vector_store(raw_text, chunk_size, chunk_overlap):
    print('chunk_size=', chunk_size, 'chunk_overlap=', chunk_overlap)
    if not raw_text:
        raise ValueError("Raw text is empty")

    # Fallback for short texts
    if len(raw_text) <= chunk_size:
        text_chunks = [raw_text]
    else:
        text_splitter = CharacterTextSplitter(separator='\n', chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                               length_function=len)
        text_chunks = text_splitter.split_text(raw_text)

    if not text_chunks:
        raise ValueError("No text chunks were created from the raw text")

    try:
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        vector_store = FAISS.from_texts(text_chunks, embeddings)
        return vector_store
    except Exception as e:
        raise RuntimeError(f"Failed to create vector store: {str(e)}")

def create_conversation_chain(vector_store, max_tokens=2550, temperature=0.3, model='gpt-3.5-turbo-16k'):
    print('TEMPERATURE',temperature)
    llm = ChatOpenAI(model=model, openai_api_key=openai.api_key, max_tokens=max_tokens, temperature=temperature)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=vector_store.as_retriever(), memory=memory)

def handle_user_input(question, conversation_chain, max_tokens):
    try:
        response = conversation_chain({'question': question})
        answer_content = response['chat_history'][-1].content

        try:
            # Intenta parsear como JSON
            parsed_content = json.loads(answer_content)
            is_json = True
        except json.JSONDecodeError:
            # Si falla, asume que no es un JSON
            parsed_content = answer_content
            is_json = False

        return parsed_content
    except Exception as e:
        return f"Error al manejar la entrada del usuario: {str(e)}"
