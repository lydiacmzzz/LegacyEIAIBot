import sys
import os
import requests
import json
import threading
import kendra_chat_bedrock_claudev2 as bedrock_claudev2
import csv

csv_file_path = 'whitelisted_users.csv'
whitelisted_users = []
try:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        
        # Iterate through each row in the CSV file
        for row in reader:
            # Assuming there is only one column in the CSV
            whitelisted_users.append(row[0])
except FileNotFoundError:
    print(f"Error: File '{csv_file_path}' not found.")
except Exception as e:
    print(f"Error: {e}")

print("Whitelisted Users:", whitelisted_users)

# Telegram secret access bot token
BOT_TOKEN = os.environ['TELEGRAMBOT']

chat_history = []
input = ""

def chatbot(input_text):
    
    llm_chain = bedrock_claudev2.build_chain()
    result = bedrock_claudev2.run_chain(llm_chain, input_text, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    
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
                    
                    if chat_id in whitelisted_users:                   

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
                                
                    else:
                        print("Sorry, you are not whitelisted")
                        if 'reply_to_message' not in result['message']:
                            bot_response = "Sorry, you are not whitelisted"
                            # Sending back response to telegram group
                            print(telegram_bot_sendtext(bot_response, chat_id, msg_id))

                            #logging
                            log = "Requestor: " + user_name + "\nQuestion: " + question + "\nAnswer: " + bot_response
                            print(telegram_bot_sendlog(log)) 

                        # Verifying that the user is responding to the ChatGPT bot
                        if 'reply_to_message' in result['message']:
                            if result['message']['reply_to_message']['from']['is_bot']:
                                bot_response = "Sorry, you are not whitelisted"
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