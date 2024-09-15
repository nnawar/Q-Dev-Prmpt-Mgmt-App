import streamlit as st
import boto3
import json
import os
import logging
from botocore.exceptions import ClientError
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state to store conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to initialize the Bedrock client
def get_bedrock_client():
    try:
        # Attempt to create a Bedrock client
        # This assumes AWS credentials are set up in the environment or through AWS CLI
        bedrock = boto3.client(service_name='bedrock-runtime')
        return bedrock
    except ClientError as e:
        logger.error(f"Error creating Bedrock client: {e}")
        st.error("Failed to connect to Amazon Bedrock. Please check your AWS credentials.")
        return None


# Function to send message to LLM and get response
async def get_llm_response(bedrock, model_id, prompt):
    try:
        # Prepare the request body based on the model
        if "anthropic.claude" in model_id:
            body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 500,
                "temperature": 0.7,
                "top_p": 0.9,
            })
        elif "amazon.titan" in model_id:
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.7,
                    "topP": 0.9,
                }
            })
        else:
            raise ValueError(f"Unsupported model: {model_id}")

        # Send request to Bedrock
        response = await asyncio.to_thread(
            bedrock.invoke_model,
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )

        # Parse and return the response
        response_body = json.loads(response.get('body').read())
        if "anthropic.claude" in model_id:
            return response_body.get('completion')
        elif "amazon.titan" in model_id:
            return response_body.get('results')[0].get('outputText')
    except ClientError as e:
        logger.error(f"Error invoking Bedrock model: {e}")
        return f"Error: {str(e)}"


# Create an Agents for Amazon Bedrock client
client = boto3.client(service_name="bedrock-agent")

# Get the list of prompts
response = client.list_prompts()

prompt_ids = []
admin_prompts = []  # Array to store all prompt template strings

if 'promptSummaries' in response:
    prompt_summaries = response['promptSummaries']
    for summary in prompt_summaries:
        if 'id' in summary:
            prompt_ids.append(summary['id'])

print(f"Extracted Prompt IDs: {prompt_ids}")
print(f"Number of Prompt IDs extracted: {len(prompt_ids)}")

# Iterate through prompt_ids and get details for each prompt
for prompt_id in prompt_ids:
    prompt_response = client.get_prompt(promptIdentifier=prompt_id)
    print(f"\nDetails for Prompt ID: {prompt_id}")
        
    # Extract the prompt template string
    prompt_template_string = None
    if 'variants' in prompt_response:
        # Assuming the first variant is the default one if 'defaultVariant' is not specified
        default_variant = prompt_response['variants'][0]
        if 'templateConfiguration' in default_variant:
            template_config = default_variant['templateConfiguration']
            if 'text' in template_config and 'text' in template_config['text']:
                prompt_template_string = template_config['text']['text']
        
    if prompt_template_string:
        print(f"Prompt Template String: {prompt_template_string}")
        admin_prompts.append(prompt_template_string)  # Add to the array
    else:
        print("Prompt Template String: Not found in the expected structure")
        


# Main function to run the Streamlit app
def main():
    st.title("AI Chat Application")

    # Initialize Bedrock client
    bedrock = get_bedrock_client()
    if not bedrock:
        return

    # LLM model selection
    model_options = {
        "Claude": "anthropic.claude-v2",
        "Titan": "amazon.titan-text-express-v1"
    }
    selected_model = st.selectbox("Choose a model", list(model_options.keys()))
   
   
    # User's favorite prompts (simulated - in a real app, this would be stored persistently)
    user_favorites = [
        "Tell me a joke",
        "What's the weather like today?"
    ]

    # Combine admin prompts and user favorites
    all_prompts = ["Select a prompt..."] + admin_prompts + ["--- Favorites ---"] + user_favorites

    # Prompt selection dropdown
    selected_prompt = st.selectbox("Select a prompt or enter your own", all_prompts)

    # User input field
    user_input = st.text_input("Enter your message:", value=selected_prompt if selected_prompt != "Select a prompt..." else "")

    # Send button
    if st.button("Send"):
        if user_input:
            # Add user message to conversation history
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Display loading indicator
            with st.spinner("AI is thinking..."):
                # Get response from LLM
                response = asyncio.run(get_llm_response(bedrock, model_options[selected_model], user_input))

            # Add AI response to conversation history
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # Save conversation button
    if st.button("Save Conversation"):
        try:
            with open("conversation_history.json", "w") as f:
                json.dump(st.session_state.messages, f)
            st.success("Conversation saved successfully!")
        except IOError as e:
            logger.error(f"Error saving conversation: {e}")
            st.error("Failed to save conversation. Please try again.")

    # Load conversation button
    if st.button("Load Conversation"):
        try:
            with open("conversation_history.json", "r") as f:
                st.session_state.messages = json.load(f)
            st.success("Conversation loaded successfully!")
            st.rerun()
        except IOError as e:
            logger.error(f"Error loading conversation: {e}")
            st.error("Failed to load conversation. File might not exist or be accessible.")

if __name__ == "__main__":
    main()
    
