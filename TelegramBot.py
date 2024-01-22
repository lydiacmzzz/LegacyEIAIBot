# from dotenv import load_dotenv
# load_dotenv()
import openai
import sys
import os
import requests
import json
import threading
import kendra_chat_bedrock_claudev2 as bedrock_claudev2


# Telegram secret access bot token
BOT_TOKEN = os.environ['TELEGRAMBOT']

# openai.api_type = "azure"
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
# openai.api_version = "2023-03-15-preview"
# openai.api_key = os.getenv("AZURE_OPENAI_KEY")

# print("Azure OpenAi Endpoint :" + openai.api_base)
# print("Azure OpenAi Key : " + openai.api_key)

chat_history = []
input = ""

def chatbot(input_text):
    #index = GPTSimpleVectorIndex.load_from_disk('index.json')
    
    llm_chain = bedrock_claudev2.build_chain()
    result = bedrock_claudev2.run_chain(llm_chain, input_text, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    
    # response = openai.ChatCompletion.create(
    #   engine="gpt35-turbo-poc001",
    #   messages = [
    #       {"role":"system","content":"Assistant is a large language model trained by OpenAI."},
    #       {"role":"user","content":input_text}],
    #   temperature=0.7,
    #   max_tokens=800,
    #   top_p=0.95,
    #   frequency_penalty=0,
    #   presence_penalty=0,
    #   stop=None)
  
#     print(response)
#     print(response['choices'][0]['message']['content'])
    
#     reply = response['choices'][0]['message']['content']
    
    return answer

def construct_username(result):
    # first_name = ""
    # last_name = ""
    username = ""
    # try:
    #     first_name = result['message']['from']['first_name']
    # except:
    #     print("firstname list not found")
 
    # try :
    #     last_name = result['message']['from']['last_name']
    # except:
    #     print("lastname list not found")

    try :
        username = result['message']['from']['username']
    except:
        print("username list not found")

    # user_name = first_name + " " +  last_name + "/" + username 
    user_name = username 
    
    return user_name            


# 3a. Function that sends a message to a specific telegram group
def telegram_bot_sendtext(bot_message,chat_id,msg_id):
    data = {
        'chat_id': chat_id,
        'text': bot_message,
        'reply_to_message_id': msg_id
    }
    response = requests.post(
        'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
        json=data
    )
    return response.json()

def telegram_bot_sendlog(bot_message):
    data = {
        'chat_id': 638740191,
        'text': bot_message
    }
    response = requests.post(
        'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
        json=data
    )
    return response.json()

# 4. Function that retrieves the latest requests from users in a Telegram group, 
# generates a response using OpenAI, and sends the response back to the group.

def Chatbot():
    # Retrieve last ID message from text file for ChatGPT update
    cwd = os.getcwd()
    filename = cwd + '/chatgpt.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")
    else:
        print("File Exists")    

    with open(filename) as f:
        last_update = f.read()
        
    # Check for new messages in Telegram group
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}'
    response = requests.get(url)
    data = json.loads(response.content)
        
    for result in data['result']:
        try:
            # Checking for new message
            if float(result['update_id']) > float(last_update):
                # Checking for new messages that did not come from chatGPT
                if "private" == result['message']['chat']['type']:
                    print("Private Chat")
                    last_update = str(int(result['update_id']))
                    
                    # Retrieving message ID of the sender of the request
                    msg_id = str(int(result['message']['message_id']))
                    
                    # Retrieving the chat ID 
                    chat_id = str(result['message']['chat']['id'])
                    
                    user_name = construct_username(result)

                    question = result['message']['text']
                    
                    print(msg_id,chat_id,user_name,question)
                    
                    # Checking that user mentionned chatbot's username in message
                    #if '@SAO_GenAi_bot' in result['message']['text']:
                    #prompt = result['message']['text'].replace("@SAO_GenAi_bot", "")
                
                    # Calling OpenAI API using the bot's personality
                    #bot_response = openAI(f"{BOT_PERSONALITY}{prompt}")
                    if 'reply_to_message' not in result['message']:
                        prompt = result['message']['text']
                        bot_response = chatbot(prompt)
                        # Sending back response to telegram group
                        print(telegram_bot_sendtext(bot_response, chat_id, msg_id))
                        
                        #logging
                        log = "Requestor: " + user_name + "\nQuestion: " + question + "\nAnswer: " + bot_response
                        print(telegram_bot_sendlog(log)) 
                        
                    # Verifying that the user is responding to the ChatGPT bot
                    if 'reply_to_message' in result['message']:
                        if result['message']['reply_to_message']['from']['is_bot']:
                            prompt = result['message']['text']
                            #bot_response = openAI(f"{BOT_PERSONALITY}{prompt}")
                            bot_response = chatbot(prompt)
                            print(telegram_bot_sendtext(bot_response, chat_id, msg_id))

                            #logging
                            log = "Requestor: " + user_name + "\nQuestion: " + question + "\nAnswer: " + bot_response
                            print(telegram_bot_sendlog(log))
                            
        except Exception as e: 
            print(e)

    # Updating file with last update ID
    with open(filename, 'w') as f:
        f.write(last_update)
    
    return "done"


# 5 Running a check every 5 seconds to check for new messages
def main():
    timertime=2
    Chatbot()
   
    # 5 sec timer
    threading.Timer(timertime, main).start()

# Run the main function
if __name__ == "__main__":
    main()