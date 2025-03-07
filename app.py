import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from groq import Groq

# Initialize the Grok client
# You'll need to set your GROQ_API_KEY as an environment variable or pass it directly here
client = Groq(api_key="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")  # Replace with your actual API key

# Function to get response from Grok
def get_grok_response(conversation_history):
    # Convert conversation history to the format expected by Groq
    messages = [{"role": "user" if isinstance(msg, HumanMessage) else "assistant", 
                 "content": msg.content} 
                for msg in conversation_history]
    
    # Call Grok API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # You can change this to another Grok model if desired
        messages=messages,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Streamlit UI
def main():
    st.title("Grok Chatbot")
    st.write("Ask me anything! Type your question below:")

    # Initialize session state to store conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # Input field for user question
    user_input = st.text_input("Your Question:", key="user_input")

    # Button to submit the question
    if st.button("Ask"):
        if user_input:
            # Add user input as a HumanMessage to the history
            human_message = HumanMessage(content=user_input)
            st.session_state.conversation_history.append(human_message)

            # Get Grok's response
            ai_response = get_grok_response(st.session_state.conversation_history)

            # Add AI response as an AIMessage to the history
            ai_message = AIMessage(content=ai_response)
            st.session_state.conversation_history.append(ai_message)

            # Display the response
            st.write("**Grok:**", ai_response)

    # Optional: Display conversation history
    if st.checkbox("Show Conversation History"):
        st.write("### Conversation History")
        for msg in st.session_state.conversation_history:
            if isinstance(msg, HumanMessage):
                st.write(f"**You:** {msg.content}")
            else:
                st.write(f"**Grok:** {msg.content}")

if __name__ == "__main__":
    main()