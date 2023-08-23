import os

from dotenv import load_dotenv
import streamlit as st
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import BingSearchAPIWrapper
from streamlit_chat import message


# 環境変数の読み込み
load_dotenv()


# クリアボタンの定義
def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button:
        chat_history = []
        if "memory" in st.session_state:
            del st.session_state["memory"]

# アプリ全体        
def main():   
    # ChatGPT-3.5のモデルのインスタンスの作成
    chat = AzureChatOpenAI(
        openai_api_base = os.getenv("OPENAI_API_BASE"),
        openai_api_version = os.getenv("OPENAI_API_VERSION"),
        deployment_name = os.getenv("OPENAI_API_MODEL_DEPROY"),
        openai_api_key = os.getenv("OPENAI_API_KEY"),
        openai_api_type = os.getenv("OPENAI_API_TYPE"),
    )

    # bingエンジンを使えるようにtoolsを定義
    #BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")
    #BING_SEARCH_URL = os.getenv("BING_SEARCH_URL")
    #BING_CUSTOM_SEARCH_ENDPOINT = os.getenv("BING_CUSTOM_SEARCH_ENDPOINT")
    #BING_CUSTOM_CONFIG = os.getenv("BING_CUSTOM_CONFIG")

    #search = BingSearchAPIWrapper()

    search = DuckDuckGoSearchRun()

    tools = [
        Tool(
            name = "BingSearch",
            func = search.run,
            description= "ウェブで最新の情報を検索する必要がある場合に便利です。",
        ) 
    ]   

    # セッション内に保存されたチャット履歴のメモリの取得
    try:
        memory = st.session_state["memory"]
    except:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

    system_message = """
    You are an Informatica expert.
    
    Answer the following questions as best you can, but speaking Japanese.
    """

    # チャット用のチェーンのインスタンスの作成
    agent = initialize_agent(
        tools=tools,
        llm=chat,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={"system_message": system_message},
        handle_parsing_errors=True,    
    )

    # Streamlitによって、タイトル部分のUIをの作成
    st.title("Chatbot with OpenAI")
    st.caption("testのチャットです")
    
    # クリアボタンの追加
    init_messages()

    # 入力フォームと送信ボタンのUIの作成
    with st.form("None", clear_on_submit=True):
        text_input = st.text_area("Enter your message",height=100)
        send_button = st.form_submit_button("Send")
        
    # チャット履歴（HumanMessageやAIMessageなど）を格納する配列の初期化
    chat_history = []
    
    # ボタンが押された時、OpenAIのAPIを実行
    if send_button:
        send_button = False

        # ChatGPTの実行
        agent.run(text_input)

        # セッションへのチャット履歴の保存
        st.session_state["memory"] = memory

        # チャット履歴（HumanMessageやAIMessageなど）の読み込み
        try:
            chat_history = memory.load_memory_variables({})["chat_history"]
        except Exception as e:
            st.error(e)

    # チャット履歴の表示
    for chat_message in reversed(chat_history):
        if type(chat_message) == HumanMessage:
            with st.chat_message('user'):
                st.markdown(chat_message.content)
        elif type(chat_message) == AIMessage:
            with st.chat_message('assistant'):
                st.markdown(chat_message.content)
                 
if __name__ == '__main__':
    main()                                     