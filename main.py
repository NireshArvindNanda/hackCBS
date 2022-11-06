from WhatsappBot import *
from message_process import *
import sqlite3

w = WhatsappBot()


conn = sqlite3.connect('productivity.sqlite')
curr = conn.cursor()
reply_list = {'Nanda':1,'Arvind':2}
commands = ['leaderboard','book follow up','word follow up','article follow up','give 5 words','day wise pts','wake up graph','weight graph']

while True:
    if w.newMessagesThere():
        w.lookForNewMessages()
        messages =  w.getNewMessages()
        print(messages)
        for msg in messages:
            group_or_personal_chat = msg[0]
            if group_or_personal_chat == 'Personal Chat':
                username = msg[1]
                phone_number = msg[2]
                if username in reply_list.keys():
                    user_id = reply_list[username]
                    new_messages = msg[-1]
                    for new_message in new_messages:
                        wt_msg = new_message[-1]
                        command = None
                        if wt_msg.strip().lower() in commands:
                            command = wt_msg.strip().lower()
                        reply = process_response(curr, conn, username, user_id, wt_msg, command)
                        conn.commit()
                        send_to, response_type, file_location, response_msg = reply
                        if send_to == 0 and response_type == 0:
                            w.sendText(username,response_msg)
                        if send_to == 0 and response_type == 1:
                            w.sendImage(username,file_location)
                        if send_to == 1 and response_type == 0:
                            w.sendTextToGroup('hackCBS Productivity',response_msg)
                        if send_to == 1 and response_type == 1:
                            w.sendImageToGroup('hackCBS Productivity',file_location)
