# ai-venturer-app



export AWS_DEFAULT_REGION=""
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""

export KENDRA_INDEX_ID=""
export S3_DATA_SOURCE_ID=""
export S3_BUCKET_NAME="aiventurers-bucket-20240121"
export FALCON_40B_ENDPOINT="<YOUR-FALCON-ENDPOINT-NAME>" 
export LLAMA_2_ENDPOINT=“<YOUR-SAGEMAKER-ENDPOINT-FOR-LLAMA2>”

streamlit run Login.py bedrock_claudev2 falcon llama2