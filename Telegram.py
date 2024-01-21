import streamlit as st
import kendra_chat_bedrock_claudev2 as bedrock_claudev2

chat_history = []
input = ""

def handle_input():
    llm_chain = bedrock_claudev2.build_chain()
    result = bedrock_claudev2.run_chain(llm_chain, input, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    answer
    result['source_documents']

input = st.text_input(label="", placeholder="You are talking to an AI, ask any question.", key="input", on_change=handle_input)