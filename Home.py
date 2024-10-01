import os
import utils
import streamlit as st
from streaming import StreamHandler

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


st.set_page_config(page_title="Vocabulary Assistant", page_icon="🤖")
st.header('Vocabulary Assistant chatbot')
st.write('Enhancing Vocabulary with Chatbot Interactions through Context Awareness')
st.write("""
[![view source code ](https://img.shields.io/badge/GitHub%20Repository-gray?logo=github)](https://github.com/Dfreequark/vocabulary_assistant/)
[![linkedin ](https://img.shields.io/badge/Kaushik%20Kashyap-blue?logo=linkedin&color=gray)](https://www.linkedin.com/in/kaushik-kashyap-80410a18a/)

""")

os.environ["COHERE_API_KEY"] = utils.user_api_key()


# Define prompt
def generate_prompt():
    system_prompt = """ You are an excellent english novel writter and vocabulary improvement coach.You provide vocabulary-related assistance based on user queries about:  words, definitions, synonyms, antonyms, example sentences, words origin, quiz. Answer user questions regarding english vocabulary within 10-20 words.
     
    RULES YOU SHOULD FOLLOW WHILE ANSWERING:  
    
    ANSWER user queries based on user vocabulary level on a scale [1,2,3,4,5,6,7,8,9,10] where 1 being beginner or lowest or easiest and 10 being procient english user or hardest. If user say level 1, provide him easy words and continously increase the difficulty level based on user level selection. 
    
    If the user provide some <word or words>, give him ONLY the meaning of the words in the format ***<input: user words> <output: words meaning, > ***

    If user ask meaning in a input language, provide meanings in that language in the example format ***<input: Give me meaning of the words in hindi language > <output: words meaning in hindi > ***

    If user <ask words>, ONLY provide 5 words with meaning and pronounciation based on his vocabulary level in the format ***<input: give me some words of level 3> <output: provide 5 words of level 3 difficulty with meaning ,> ***.

    If user <ask about definitions, synonyms, antonyms, example sentences>, provide him answer with the words already mentioned or if not provided , ask him to provide words in the format ***<input: give me examples/details/paragraphs/synonyms/antonyms/origin> <output: provide required answer> ***.

    Please remember,FOR QUIZ AND QUIZ ONLY, If user ask about quiz then and only then, You will ONLY provide the user a vocabulary quiz.. Give a sentence using a word that is being discussed and with 4 different options where ONLY one is correct answer in the format:<output:
                Quiz: <Your Question Here>\n <pronounciation of the word>
                Options:\n
                A) <Option 1>\n
                B) <Option 2>\n
                C) <Option 3>\n
                D) <Option 4>\n >

    Formats of output content:
    If user intention is quiz, provide output in BLOCK Snippet Style with main vocabulary as BLUE colored. Otherwise provide output in TABLE Snippet Style.



    Don't give answer to the quiz. Only answer when user select one of the options with the correct answer and explain it if user provide incorrect answer. THINK BEFORE YOU ANSWER.

    Don't extend output without user queries. After providing quiz answer, stop there. Wait for user input queries.

    
    If the user asks any questions outside of vocabulary improvement, politely inform them that you are only able to assist with vocabulary improvement.
             """

    # prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("user", "Question: {input}"),
            
        ]
    )
    return prompt

class ContextChatbot:


    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        
    def set_level(self):
        with st.sidebar:
            level = st.slider("Select difficulty level?", 1, 10, 3)
        return level
    
    def clear_memory(self):
        # Clear values from *all* all in-memory and on-disk data caches:
        with st.sidebar:
            if st.button("Clear Memory"):
                try:
                    st.cache_resource.clear()
                    del st.session_state["current_page"]
                    del st.session_state["messages"]
                except:
                    pass

    @st.cache_resource
    def setup_chain(_self):
        prompt = generate_prompt()
        memory = ConversationBufferMemory(return_messages=True)
        chain = ConversationChain(llm=_self.llm,prompt= prompt ,memory=memory ,verbose=False)
        return chain
    
    @utils.enable_chat_history
    def main(self):
        self.clear_memory()
        chain = self.setup_chain()
        level = self.set_level()
        user_query = st.chat_input(placeholder="Ask me anything!")
        with st.sidebar:
            st.write("Choose Option:")
            left, right = st.columns(2)
            Words = left.button('Words!')
            Details = right.button('Details!')
            Examples = left.button('Examples!')
            Paragraph = right.button('Paragraph!')
            Synonyms = left.button('Synonyms!')
            Antonyms = right.button('Antonyms!')
            Etymology = left.button('Etymology!')
            TestMe = right.button('Take a quiz!')

            st.write("Get meaning of words in your mother tounge:")
            language = st.text_input("Enter your language")
            


        if Words:
            user_query =f"Give me some new words of level {level}."
        elif Details:
            user_query ="Give me more details about the words: what are the use cases of them "
        elif Examples:
            user_query =f"Give example sentence "
        elif Paragraph:
            user_query ="Write a short paragraph using the words"
        elif Synonyms:
            user_query ="Give synonyms for each word"
        elif Antonyms:
            user_query ="Give antonyms for each word"
        elif Etymology:
            user_query ="Give roots or origin of the words(Etymology)"
        elif TestMe:
            user_query =f"Give me a quiz of the words we discussed."
        
        elif language:
                user_query =f"Give me meaning of the words in {language} language."
        
        

        if user_query:
            st.chat_message("user").write(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = chain.invoke(
                    {"input":user_query},
                    {"callbacks": [st_cb]}
                )
                
                
                response = result["response"]
                st.session_state.messages.append({"role": "assistant", "content": response})


                

if __name__ == "__main__":
    obj = ContextChatbot()
    obj.main()