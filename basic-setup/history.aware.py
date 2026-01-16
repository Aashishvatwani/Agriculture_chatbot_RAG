from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()
persistent_directory="db/chroma_db"
embedding_model=OpenAIEmbeddings(model="text-embedding-3-small")
model = ChatOpenAI(model="gpt-4o")
load_dotenv()
db=Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space":"cosine"}
)
chat_history=[]

def generate_response(user_input):
    """
    Minimal response generator: records the user's message and returns a simple placeholder reply.
    Replace this with actual retrieval/LLM logic when ready.
    """
    # record the user's message in the history
    chat_history.append(HumanMessage(content=user_input))
    # generate a simple placeholder reply (could be replaced by model.generate/ask logic)
    reply = f"Received: {user_input}"
    chat_history.append(AIMessage(content=reply))
    return reply

def start_chat():
    print("Chat session started. Type 'exit' to end the session.")
    while True:
        user_input = input("User: ")
        if user_input.lower() == 'exit':
            print("Chat session ended.")
            break
        response = generate_response(user_input)
        print(f"Assistant: {response}")