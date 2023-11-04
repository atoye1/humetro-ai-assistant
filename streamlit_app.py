# code from https://python.langchain.com/docs/integrations/callbacks/streamlit?ref=blog.langchain.dev#installation-and-setup
import openai
import os

from llm_tools.GoogleRoutes import GoogleRouteTool
from llm_tools.HumetroFareTool import HumetroFareTool
from llm_tools.HumetroWebSearchTool import HumetroWebSearchTool
from mongo_db import save_to_mongo

import langchain
langchain.debug= True

from langchain.chat_models import ChatOpenAI
from langchain.prompts  import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents import  OpenAIFunctionsAgent, AgentExecutor, OpenAIMultiFunctionsAgent
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from dotenv import load_dotenv, find_dotenv

import streamlit as st
from llm_tools.prompts import humetro_system_prompt
# from audiorecorder import AudioRecorder, audiorecorder
# from gtts import gTTS

from capturing_callback_handler import playback_callbacks
from clear_results import with_clear_container
from streamlit_agent import haa_executor

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

st.set_page_config(page_title="Humetro-AI-Assistant",
                   page_icon="🤖")

if 'langchain_messages' not in st.session_state:
    st.session_state.langchain_messages = []

chat_history = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(memory_key='history', chat_memory=chat_history)

if len(chat_history.messages)  == 0:
    chat_history.add_ai_message("안녕하세요 하단역의 인공지능 어시스턴트입니다. 궁금한 것이 있으시면 물어보세요!")

st.write("# 🚇 Humetro AI Assistant")
st.write("### 🤖 인공지능 어시스턴트에게 질문해보세요!")

st.write(st.session_state)

output_container = st.empty()
answer_container = st.empty()

output_container = output_container.container()
for msg in st.session_state.langchain_messages:
    output_container.chat_message(msg.type).write(msg.content)

if user_input := st.chat_input('이곳에 질문을 입력하세요.'):
    output_container.chat_message("user").write(user_input)

    answer_container = output_container.chat_message("assistant")
    st_callback = StreamlitCallbackHandler(answer_container)

    answer = haa_executor.run({"input":user_input}, callbacks=[st_callback])
    answer_container.write(answer)

    # 메시지를 메시지를 보관하는 세션에 저장한다.
    chat_history.add_user_message(user_input)
    chat_history.add_ai_message(answer)
    save_to_mongo(user_input, answer)

# if audio_input := st.audio_recorder("audio.wav"):
#     output_container = output_container.container()
#     output_container.chat_message("user").write(audio_input)

#     answer_container = output_container.chat_message("assistant")
#     st_callback = StreamlitCallbackHandler(answer_container)

#     answer = haa.run(audio_input, callbacks=[st_callback])
#     answer_container.write(answer)

#     save_to_mongo(audio_input, answer)

view_messages = st.expander("**모든 대화 목록  확인하기(클릭)**")
with view_messages:
    view_messages.json(st.session_state.langchain_messages)