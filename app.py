import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from groq import Groq
import os

# Initialize session state for API key and client
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "client" not in st.session_state:
    st.session_state.client = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Function to get response from Groq
def get_groq_response(conversation_history):
    # Convert conversation history to the format expected by Groq
    messages = [{"role": "user" if isinstance(msg, HumanMessage) else "assistant", 
                 "content": msg.content} 
                for msg in conversation_history]
    
    # Call Groq API
    response = st.session_state.client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Function to validate API key
def validate_api_key(api_key):
    try:
        # Set the API key as an environment variable
        os.environ["GROQ_API_KEY"] = api_key
        # Create the client
        client = Groq()
        # Make a test API call
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return True, client
    except Exception as e:
        return False, str(e)

# Streamlit UI
def main():
    st.title("Groq Chatbot")
    
    # API Key input
    if not st.session_state.api_key:
        st.write("Please enter your Groq API key to start:")
        api_key = st.text_input("Groq API Key:", type="password")
        if api_key:
            # Validate the API key
            is_valid, result = validate_api_key(api_key)
            if is_valid:
                st.session_state.client = result
                st.session_state.api_key = api_key
                st.success("API key validated successfully!")
                st.experimental_rerun()  # Force a rerun to show the chat interface
            else:
                st.error(f"Invalid API key: {result}")
                return
    else:
        st.write("Ask me anything! Type your question below:")

        # Input field for user question
        user_input = st.text_input("Your Question:", key="user_input")

        # Button to submit the question
        if st.button("Ask"):
            if user_input:
                try:
                    # Add user input as a HumanMessage to the history
                    human_message = HumanMessage(content=user_input)
                    st.session_state.conversation_history.append(human_message)

                    # Get Groq's response
                    ai_response = get_groq_response(st.session_state.conversation_history)

                    # Add AI response as an AIMessage to the history
                    ai_message = AIMessage(content=ai_response)
                    st.session_state.conversation_history.append(ai_message)

                    # Display the response
                    st.write("**Groq:**", ai_response)
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")
                    if "401" in str(e):
                        st.error("Authentication error. Please check your API key and try again.")
                        st.session_state.api_key = None
                        st.session_state.client = None
                        if "GROQ_API_KEY" in os.environ:
                            del os.environ["GROQ_API_KEY"]
                        st.experimental_rerun()

        # Optional: Display conversation history
        if st.checkbox("Show Conversation History"):
            st.write("### Conversation History")
            for msg in st.session_state.conversation_history:
                if isinstance(msg, HumanMessage):
                    st.write(f"**You:** {msg.content}")
                else:
                    st.write(f"**Groq:** {msg.content}")
        
        # Add a button to reset the API key
        if st.button("Reset API Key"):
            st.session_state.api_key = None
            st.session_state.client = None
            st.session_state.conversation_history = []
            if "GROQ_API_KEY" in os.environ:
                del os.environ["GROQ_API_KEY"]
            st.experimental_rerun()

if __name__ == "__main__":
    main()