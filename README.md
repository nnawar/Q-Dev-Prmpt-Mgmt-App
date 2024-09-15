# Chat App with Prompt Management
Aside from using jupyter notebooks for ML or Quantum computing, I have no experience writing code.
This app here was built from scratch using the coding assistant: [Amazon Q Developer](https://aws.amazon.com/q/developer/).

When I say "from scratch", I loterally mean I started by asking Amazon-Q a similar prompt to this one here:

>*Guide me through what I need to provide you in order to build a streamlit application that allows users to send their prompts against a choice of amazon bedrock foundational models. The user should be able to type their prompt from scratch, or start from a list of curated administrator prompts*

## Prerequisites:
1. Python 3.9 or later
2. [Streamlit](https://docs.streamlit.io/get-started/installation)
3. Latest [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
4. Latest AWS CLI (Here is how to [install](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-install.html) and [configure](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) the CLI)

## Run
You can run the code as a Streamlit app.

`streamlit run chat_app_prmpt_mgmt.py`
