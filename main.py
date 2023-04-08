import os
import PyPDF2
import streamlit as st
from langchain.llms import OpenAIChat
from langchain.chains import LLMRequestsChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Current Model
st.title("Langchain App")

ApiKey = st.text_input('ApiKey', "", type="password")

# --------------------------------
UploadedText = ""

def extract_text(pdf_file):
    # Read PDF file
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Extract text from all pages
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += "  \nPage " + str(page_num) + ":  \n" + page.extract_text()

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

# Encapsulating the code for each option
def option1():
    # Attempt at implementing document scanning for gpt (not sucsessfully implemented)
    # see https://python.langchain.com/en/latest/modules/chains/index_examples/qa_with_sources.html
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
            template = """Try to answer the question about the provided document, if you do not know the answer, 
            say you dont: {Question}. Use this context to answer this question: {MyText}"""
            prompt = PromptTemplate(template=template, input_variables=['MyText', 'Question'])
            input = {
                'MyText': UploadedText,
                'Question': MyQuestion
                     }

            chain = LLMChain(llm=MyModel, prompt=prompt)
            st.success(chain(input)['text'])
    else:
        st.write("no api key")


def option2():
    # Attempt at implementing "websearch" for gpt,
    # see https://python.langchain.com/en/latest/modules/chains/examples/llm_requests.html
    st.write('Option 2, ask webpage')

    MyUrl = st.text_input('Webpage to search', "https://github.com/Karsten-Allison/CougHacksWack/blob/master/main.py")

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
    # Attempt at implementing "memory" for langchain (didn't work)
    # see  https://python.langchain.com/en/latest/modules/memory/examples/adding_memory.html
    st.write('Option 3, Email Advice')
    if ApiKey is not "":
        if st.button("Ask", type="primary"):
            MyModel = OpenAIChat(model_name='gpt-3.5-turbo', openai_api_key=ApiKey)

            template = """You are a bot that rewrite's emails to sound more professional.
                    Take their template email, expand on details and make it professional. You can falsify details that
                    seem unprofessional. 
                    {chat_history}
                    Human: {Question}
                    Chatbot:"""

            prompt = PromptTemplate(
                input_variables=["chat_history", "Question"],
                template=template
            )
            memory = ConversationBufferMemory(memory_key="chat_history")
            chain = LLMChain(llm=MyModel, prompt=prompt, verbose=True, memory=memory)

            st.write(chain.predict(Question=MyQuestion))

            Followup = """Give constructive criticism on a few ways I could have improved upon this task.  
            Give it in a bulleted list, start by saying: "Here's how you could have improved"
            """
            st.write(chain.predict(Question=Followup))
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



