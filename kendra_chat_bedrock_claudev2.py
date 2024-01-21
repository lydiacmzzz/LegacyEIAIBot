import boto3
import os
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock

# Global Constants
MAX_HISTORY_LENGTH = 5

# Class for color codes
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_aws_client(service_name, region, cross_account=False):
    """ Initialize an AWS client, optionally with cross-account access. """
    if cross_account:
        sts = boto3.client('sts')
        resp = sts.assume_role(
            RoleArn='arn:aws:iam::017490449790:role/WorkshopBedrockCrossAccountAccess',
            RoleSessionName='testsession'
        )
        session = boto3.Session(
            aws_access_key_id=resp['Credentials']['AccessKeyId'],
            aws_secret_access_key=resp['Credentials']['SecretAccessKey'],
            aws_session_token=resp['Credentials']['SessionToken']
        )
        return session.client(service_name, region_name=region)
    else:
        return boto3.client(service_name, region_name=region)

def build_chain():
    region = os.environ["AWS_REGION"]
    kendra_index_id = os.environ["KENDRA_INDEX_ID"]

    # Option 1: Using Bedrock subscription from another AWS account
    # Uncomment the next line for cross-account access
    # boto3_bedrock = get_aws_client('bedrock-runtime', region, cross_account=True)

    # Option 2: Using Bedrock subscription from this AWS account
    boto3_bedrock = get_aws_client('bedrock-runtime', region)

    llm = Bedrock(
        client=boto3_bedrock,
        region_name = region,
        model_kwargs={
            "max_tokens_to_sample":300,
            "temperature":1,
            "top_k":250,"top_p":0.999,
            "anthropic_version":"bedrock-2023-05-31"
        },
        model_id="anthropic.claude-v2"
      )
      
    retriever = AmazonKendraRetriever(index_id=kendra_index_id, top_k=5, region_name=region)
    
    prompt_template = """
    Human: This is a friendly conversation between a human and an AI. 
    The AI is talkative and provides specific details from its context but limits it to 240 tokens.
    If the AI does not know the answer to a question, it truthfully says it 
    does not know.

    Assistant: OK, got it, I'll be a talkative truthful AI assistant.

    Human: Here are a few documents in <documents> tags:
    <documents>
    {context}
    </documents>
    Based on the above documents, provide a detailed answer for, {question} 
    Answer "don't know" if not present in the document.
    Don't show any documents if there is no document.

    Assistant:
    """
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    condense_qa_template = """
    {chat_history}
    Human:
    Given the previous conversation and a follow up question below, rephrase the follow up question
    to be a standalone question.

    Follow Up Question: {question}
    Standalone Question:

    Assistant:
    """

    standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        condense_question_prompt=standalone_question_prompt, 
        return_source_documents=True, 
        combine_docs_chain_kwargs={"prompt":prompt},
        verbose=True)

  # qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, qa_prompt=prompt, return_source_documents=True)
    return qa

def run_chain(chain, prompt: str, history=[]):
    try:
        return chain({"question": prompt, "chat_history": history})
    except Exception as e:
        print(f"{bcolors.FAIL}Error occurred: {e}{bcolors.ENDC}")
        return None

def main():
    chat_history = []
    qa = build_chain()
    print(bcolors.OKBLUE + "Hello! How can I help you?" + bcolors.ENDC)

    while True:
        try:
            print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
            print(">", end=" ", flush=True)
            query = input()
            
            if query.lower().startswith("new search:"):
                chat_history = []
                query = query[len("new search:"):].strip()

            if len(chat_history) >= MAX_HISTORY_LENGTH:
                chat_history.pop(0)

            result = run_chain(qa, query, chat_history)
            if result:
                chat_history.append((query, result["answer"]))
                print(bcolors.OKGREEN + result['answer'] + bcolors.ENDC)
                if 'source_documents' in result:
                    print(bcolors.OKGREEN + 'Sources:')
                    for d in result['source_documents']:
                        print(d.metadata['source'])
                print(bcolors.ENDC)
            
        except EOFError:
            break

    print(bcolors.OKBLUE + "Bye" + bcolors.ENDC)

if __name__ == "__main__":
    main()