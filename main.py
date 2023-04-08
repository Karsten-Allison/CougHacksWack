import os
import PyPDF2
import streamlit as st
from langchain.llms import OpenAIChat
from langchain.chains import LLMRequestsChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Current Model
st.title("My App")

ApiKey = st.text_input('ApiKey', "")

# --------------------------------
UploadedText = ""

def extract_text(pdf_file):
    # Read PDF file
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Extract text from all pages
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += "Page " + str(page_num) + ":\n" + page.extract_text()

    return text

# ---------------------------------
MyQuestion = st.text_input('Your Question', "Can you summarize this for me?")


#Selection box to choose what to display.
option = st.sidebar.selectbox(
    'Select an option',
    ('Option 1', 'Option 2', 'Option 3')
)
container1 = st.container()
container2 = st.container()
container3 = st.container()

# Encapsulate the code for each option in a separate function
def option1():
    st.write('Option 1, ask pdf')
    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
    if pdf_file is not None:
        text = extract_text(pdf_file)
        st.header("PDF Text")
        st.write(text)
        UploadedText = extract_text(pdf_file)
    if ApiKey is not "":
        if st.button("Ask", type="primary"):
            MyModel = OpenAIChat(model_name='gpt-3.5-turbo', openai_api_key=ApiKey)
            template = """Answer this question acting as a human tutor, if you do not know the answer, 
            say you dont: {Question}. Use this context to answer this question: {MyText}"""
            prompt = PromptTemplate(template=template, input_variables=['MyText', 'Question'])
            input = {'MyText': UploadedText, 'Question': MyQuestion}

            chain = LLMChain(llm=MyModel, prompt=prompt)
            st.success(chain(input)['text'])
    else:
        st.write("no api key")


def option2():
    # Code for option 2
    st.write('Option 2, ask webpage')

    MyUrl = st.text_input('Webpage to search', "https://github.com/Karsten-Allison")

    if ApiKey is not "":
        if st.button("Ask", type="primary"):
            MyModel = OpenAIChat(model_name='gpt-3.5-turbo', openai_api_key=ApiKey)

            template = """
            Format the response from the website by extracting the answer to {query}.
            Extract the {requests_result} from the website, and use that to answer {query} if applicable.
            Your answer is:
            """

            prompt = PromptTemplate(template=template, input_variables=['requests_result', 'query'])
            chain = LLMRequestsChain(llm_chain=LLMChain(llm=MyModel, prompt=prompt))

            inputs = {
                "query": MyQuestion,
                "url":  MyUrl
            }

            st.success(chain(inputs)['output'])
    else:
        st.write("no api key")

def option3():
    # Code for option 3
    st.write('Option 3, ask')
    if ApiKey is not "":
        if st.button("Ask", type="primary"):
            MyModel = OpenAIChat(model_name='gpt-3.5-turbo', openai_api_key=ApiKey)

            template = """You are a chatbot having a conversation with a human.
        
                    {chat_history}
                    Human: {Question}
                    Chatbot:"""

            prompt = PromptTemplate(
                input_variables=["chat_history", "Question"],
                template=template
            )
            memory = ConversationBufferMemory(memory_key="chat_history")
            chain = LLMChain(llm=MyModel, prompt=prompt, verbose=True, memory=memory)

            st.write(chain.predict(Question = MyQuestion))
    else:
        st.write("no api key")


if option == 'Option 1':
    with container1:
        option1()
    container2.empty()
    container3.empty()

elif option == 'Option 2':
    with container2:
        option2()
    container1.empty()
    container3.empty()

else:
    with container3:
        option3()
    container1.empty()
    container2.empty()



