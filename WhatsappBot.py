from datetime import datetime
import pyautogui as pag
from scipy.spatial import distance
import sqlite3
import time
import pyperclip
import re
import copy
from PIL import Image
from io import BytesIO
import win32clipboard

class WhatsappBot:
    def __init__(self):
        pag.FAILSAFE = False
        self.__setupDBSchema()
        self.__whatsapp_coordinates = (395, 1022)
        self.__whatsapp_new_msg = (250, 0, 0)
        self.__whatsapp_no_new_msg = (0, 150, 150)
        self.__unread_chat_filter_coordinates = (632, 174)
        self.__unread_chat_filter_on = (0, 168, 132)
        self.__unread_chat_filter_off = (17, 27, 33)
        self.__kebab_menu_coordinates = (1866, 94)
        self.__contact_info_coordinates = (1753, 165)
        self.__contact_info_field1_coordinates = (1622, 517)
        self.__contact_info_field2_coordinates = (1626, 556)
        self.__contact_info_field2_coordinates_for_group = (1519, 558)
        self.__close_contact_info_coordinates = (1399, 94)
        self.__type_message_coordinates = (1185, 956)
        self.__first_chat_under_filter_coordinates = (333, 364)
        self.__show_desktop_coordinates = (1919, 1049)
        self.__top_left_in_chat = (713, 157)
        self.__bottom_right_in_chat = (1805, 872)
        self.__user_name_of_wt_bot = 'Niresh'
        self.__default_group = 'hackCBS Productivity'
        self.__send_message_coordinates = (1865, 959)
        self.__send_image_coordinates = (1851, 926)
        self.__whatsapp_time_format = '%H:%M, %d/%m/%Y'
        self.__time_format = '24'
        self.__width = pag.size()[0]
        self.__height = pag.size()[1]
        self.__current_open_chat = 'Nothing'
        self.__delay = 0.5
        self.__mouse_delay = 0.25
        self.__type_delay = 0.1
        self.__openWhatsApp()
        self.__goToDefaultGroup()
        self.__minimizeWhatsapp()
        self.__new_messages = []

    def __commitDBChanges(self):
        self.__conn.commit()

    def __setupDBSchema(self):
        self.__conn = sqlite3.connect('chat.sqlite')
        self.__cur = self.__conn.cursor()
        self.__cur.executescript('''

        CREATE TABLE IF NOT EXISTS USERS(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            user_name TEXT,
            is_saved_contact INTEGER
        );

        CREATE TABLE IF NOT EXISTS GROUPS(
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT
        );

        CREATE TABLE IF NOT EXISTS MESSAGE_STATUS(
            message_status_id INTEGER PRIMARY KEY,
            meaning TEXT
        );

        CREATE TABLE IF NOT EXISTS MESSAGES(
            user_id INTEGER,
            group_id INTEGER,
            date TEXT,
            message TEXT,
            message_status_id INTEGER,
            CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES USERS(user_id),
            CONSTRAINT fk_group FOREIGN KEY (group_id) REFERENCES GROUPS(group_id),
            CONSTRAINT fk_msg_status FOREIGN KEY (message_status_id) REFERENCES MESSAGE_STATUS(message_status_id)
        );          
        ''')

        self.__cur.execute('''SELECT COUNT(user_id) FROM USERS WHERE user_id=0;''')
        user_0_in_db = self.__cur.fetchone()
        if user_0_in_db[0] == 0:
            self.__cur.execute('''INSERT INTO USERS(user_id,phone_number,user_name) VALUES (0,'00000 000000','Not Applicable');''')
        self.__cur.execute('''SELECT COUNT(group_id) FROM GROUPS WHERE group_id=0;''')
        group_0_in_db = self.__cur.fetchone()
        if group_0_in_db[0] == 0:
            self.__cur.execute('''INSERT INTO GROUPS(group_id,group_name) VALUES (0,'Not Applicable');''')
        self.__cur.execute('''SELECT COUNT(meaning) FROM MESSAGE_STATUS;''')
        msg_status_in_db = self.__cur.fetchone()
        if msg_status_in_db[0] == 0:
            self.__cur.execute('''INSERT INTO MESSAGE_STATUS(message_status_id,meaning) VALUES (0,'SENT TO');''')
            self.__cur.execute('''INSERT INTO MESSAGE_STATUS(message_status_id,meaning) VALUES (1,'RECEIVED FROM');''')
        self.__commitDBChanges()

    def __userExistsInDb(self, phone_number):
        self.__cur.execute('''SELECT COUNT(user_id) FROM USERS WHERE phone_number=?;''', (phone_number,))
        user_in_db = self.__cur.fetchone()
        if user_in_db[0] == 0:
            return False
        return True

    def __addUserInDb(self, phone_number, user_name, is_saved_contact):
        self.__cur.execute('''INSERT INTO USERS(phone_number, user_name, is_saved_contact) VALUES (?,?,?);''',(phone_number, user_name, is_saved_contact))
        self.__commitDBChanges()

    def __getUserDetailsInDBWithPhone(self, phone_number):
        self.__cur.execute('''SELECT user_id, phone_number, user_name, is_saved_contact FROM USERS WHERE phone_number=?;''',(phone_number,))
        user_details = self.__cur.fetchone()
        return user_details

    def __getUserDetailsInDBWithUserName(self, user_name):
        self.__cur.execute('''SELECT user_id, phone_number, user_name, is_saved_contact FROM USERS WHERE user_name=?;''', (user_name,))
        user_details = self.__cur.fetchone()
        return user_details

    def __getUserDetailsInDBWithUserId(self, user_id):
        self.__cur.execute('''SELECT user_id, phone_number, user_name, is_saved_contact FROM USERS WHERE user_id=?;''', (user_id,))
        user_details = self.__cur.fetchone()
        return user_details

    def __updateUserDetailsInDB(self, user_name, is_saved_contact, phone_number):
        self.__cur.execute('''UPDATE USERS SET user_name=?,is_saved_contact=? WHERE phone_number=?;''',(user_name, is_saved_contact, phone_number))
        self.__commitDBChanges()

    def __getUserIdInDB(self, ph_no_or_name):
        self.__cur.execute('''SELECT user_id FROM USERS WHERE phone_number=? OR user_name=?;''', (ph_no_or_name, ph_no_or_name))
        user_id_in_list = self.__cur.fetchone()
        if user_id_in_list is None:
            return None
        return user_id_in_list[0]

    def __groupExistsInDb(self, group_name):
        self.__cur.execute('''SELECT COUNT(group_id) FROM GROUPS WHERE group_name=?;''', (group_name,))
        group_in_db = self.__cur.fetchone()
        if group_in_db[0] == 0:
            return False
        return True

    def __addGroupInDb(self, group_name):
        self.__cur.execute('''INSERT INTO GROUPS(group_name) VALUES (?);''', (group_name,))
        self.__commitDBChanges()

    def __getGroupIdInDB(self, group_name):
        self.__cur.execute('''SELECT group_id FROM GROUPS WHERE group_name=?;''', (group_name,))
        group_id_in_list = self.__cur.fetchone()
        if group_id_in_list is None:
            return None
        return group_id_in_list[0]

    def __insertMessageWithoutCommit(self, user_id, group_id, date, message, message_status_id):
        self.__cur.execute('''INSERT INTO MESSAGES(user_id, group_id, date, message, message_status_id) VALUES (?,?,?,?,?);''',
            (user_id, group_id, date, message, message_status_id))

    def __openWhatsApp(self):
        pag.leftClick(self.__whatsapp_coordinates[0], self.__whatsapp_coordinates[1], self.__mouse_delay)
        time.sleep(3 * self.__delay)

    def __minimizeWhatsapp(self):
        pag.leftClick(
            self.__show_desktop_coordinates[0], self.__show_desktop_coordinates[1], self.__mouse_delay)
        time.sleep(2 * self.__delay)

    def __goToSearchBar(self):
        pag.hotkey('ctrl', 'f')
        time.sleep(self.__delay)

    def __goToWhatsappDefaultState(self):
        self.__goToSearchBar()
        for presses in range(40):
            pag.press('backspace')
        pag.moveTo(self.__first_chat_under_filter_coordinates[0], self.__first_chat_under_filter_coordinates[1], self.__mouse_delay)
        pag.scroll(25 * self.__height)

    def __copy(self):
        pag.hotkey('ctrl', 'c')
    
    def __paste(self):
        pag.hotkey('ctrl', 'v')

    def __emptyClipBoard(self):
        pyperclip.copy('')
    
    def __copyTextToClipBoard(self, text):
        pyperclip.copy(text)

    def __getContactOrGroupInfo(self):
        pag.leftClick(self.__kebab_menu_coordinates[0], self.__kebab_menu_coordinates[1], self.__mouse_delay)
        time.sleep(3 * self.__delay)
        pag.leftClick(self.__contact_info_coordinates[0], self.__contact_info_coordinates[1], self.__mouse_delay)
        time.sleep(3 * self.__delay)

        pag.tripleClick(self.__contact_info_field2_coordinates_for_group[0], self.__contact_info_field2_coordinates_for_group[1])
        time.sleep(self.__delay)
        self.__copy()
        field2 = pyperclip.paste()

        pag.tripleClick(self.__contact_info_field1_coordinates[0], self.__contact_info_field1_coordinates[1])
        time.sleep(self.__delay)
        self.__copy()
        field1 = pyperclip.paste()

        if field2.lower().startswith('group'):
            group_name = field1
            if self.__groupExistsInDb(group_name):
                group_id = self.__getGroupIdInDB(group_name)
            else:
                self.__addGroupInDb(group_name)
                group_id = self.__getGroupIdInDB(group_name)
            pag.leftClick(self.__close_contact_info_coordinates[0], self.__close_contact_info_coordinates[1], self.__mouse_delay)
            time.sleep(2 * self.__delay)
            return ['Group Chat', group_id, group_name]

        pag.tripleClick(self.__contact_info_field2_coordinates[0], self.__contact_info_field2_coordinates[1])
        time.sleep(self.__delay)
        self.__copy()
        field2 = pyperclip.paste()

        pag.leftClick(self.__close_contact_info_coordinates[0], self.__close_contact_info_coordinates[1], self.__mouse_delay)
        time.sleep(2 * self.__delay)
        if field2.startswith('~'):
            is_saved_contact = 0
            phone_number = field1
            user_name = field2[1:]
        else:
            is_saved_contact = 1
            phone_number = field2
            user_name = field1

        if self.__userExistsInDb(phone_number) is False:
            self.__addUserInDb(phone_number, user_name, is_saved_contact)
            user_id_in_db = self.__getUserIdInDB(phone_number)
            return ['Personal Chat', user_id_in_db, user_name, phone_number, is_saved_contact]

        user_id_in_db, phone_number_in_db, user_name_in_db, is_saved_contact_in_db = self.__getUserDetailsInDBWithPhone(
            phone_number)
        if user_name_in_db != user_name or is_saved_contact != is_saved_contact_in_db:
            self.__updateUserDetailsInDB(
                user_name, is_saved_contact, phone_number)
        return ['Personal Chat', user_id_in_db, user_name, phone_number, is_saved_contact]

    def __openChat(self, ph_no_or_name):
        if self.__insideSameChat(ph_no_or_name):
            return
        self.__goToWhatsappDefaultState()
        self.__goToSearchBar()
        pag.typewrite(ph_no_or_name, self.__type_delay)
        pag.moveTo(self.__first_chat_under_filter_coordinates[0], self.__first_chat_under_filter_coordinates[1], self.__mouse_delay)
        pag.scroll(25 * self.__height)
        time.sleep(self.__delay)
        pag.leftClick(self.__first_chat_under_filter_coordinates[0], self.__first_chat_under_filter_coordinates[1],self.__mouse_delay)
        time.sleep(3 * self.__delay)
        self.__current_open_chat = copy.deepcopy(ph_no_or_name)

    def __getContactOrGroupInfoOf(self, ph_no_or_name):
        self.__openChat(ph_no_or_name)
        contact_info = self.__getContactOrGroupInfo()
        self.__current_open_chat = copy.deepcopy(contact_info)
        return contact_info

    def __retrieveUserInfo(self, ph_no_or_name):
        user_info = self.__getUserDetailsInDBWithPhone(ph_no_or_name)
        if user_info is not None:
            return user_info
        user_info = self.__getUserDetailsInDBWithUserName(ph_no_or_name)
        if user_info is not None:
            return user_info
        self.__getContactOrGroupInfoOf(ph_no_or_name)
        user_info = self.__getUserDetailsInDBWithPhone(ph_no_or_name)
        if user_info is not None:
            return user_info
        user_info = self.__getUserDetailsInDBWithUserName(ph_no_or_name)
        if user_info is not None:
            return user_info

    def __goToDefaultGroup(self):
        self.__openChat(self.__default_group)

    def goToProductivityGroup(self):
        self.__openChat('hackCBS Productivity')

    def __deselectSelectedText(self):
        x = self.__type_message_coordinates[0]
        y = self.__type_message_coordinates[1]
        pag.leftClick(x, y, self.__mouse_delay)
        time.sleep(self.__delay)

    def __selectAndCopyMessages(self, scroll_length):
        x1 = self.__top_left_in_chat[0]
        y1 = self.__top_left_in_chat[1]
        x2 = self.__bottom_right_in_chat[0]
        y2 = self.__bottom_right_in_chat[1]
        pag.moveTo(int((x1+x2)*0.5), int((y1 + y2) * 0.5), self.__mouse_delay)
        pag.scroll(-25 * self.__height)
        some_msg_selected = False

        while y1 + 10 < y2 and some_msg_selected is False:
            pag.mouseDown(x2, y2, 'left', self.__mouse_delay)
            pag.moveTo(x1, int(y1 + (y2 - y1) * 0.2), self.__mouse_delay)
            pag.mouseUp(None, None, 'left')
            self.__emptyClipBoard()
            self.__copy()
            selected_text = pyperclip.paste()
            self.__deselectSelectedText()
            if selected_text == '':
                y2 -= 3
            else:
                some_msg_selected = True

        if some_msg_selected == False:
            return ''

        pag.mouseDown(x2, y2, 'left', self.__mouse_delay)
        pag.moveTo(x1, int(y1 + (y2 - y1) * 0.2), self.__mouse_delay)
        time.sleep(self.__delay)
        pag.scroll(scroll_length + self.__height)
        time.sleep(self.__delay)
        pag.moveTo(x1, y1, self.__mouse_delay)
        pag.mouseUp(None, None, 'left')
        self.__emptyClipBoard()
        self.__copy()
        selected_text = pyperclip.paste()
        self.__deselectSelectedText()
        return selected_text

    def __getLastMsgFromGrp(self, group_id):
        self.__cur.execute('SELECT user_id,group_id,date,message,message_status_id FROM MESSAGES WHERE group_id = ? ORDER BY date DESC LIMIT 1;', (group_id,))
        details = self.__cur.fetchone()
        if details is None:
            return None

        user_id, group_id, date_time_string, message, message_status_id = details
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.strptime(date_time_string, format_in_db)

        date_time_string = (date_time_object.strftime(self.__whatsapp_time_format)).lower()
        if date_time_string[0] == '0' and self.__time_format == '12':
            date_time_string = date_time_string[1:]

        wt_exported_format_of_last_msg = '[' + date_time_string + '] '
        if int(message_status_id) == 0:
            wt_exported_format_of_last_msg += self.__user_name_of_wt_bot
        else:
            user_id, phone_number, user_name, is_saved_contact = self.__getUserDetailsInDBWithUserId(user_id)
            if int(is_saved_contact) == 1:
                wt_exported_format_of_last_msg += user_name
            else:
                wt_exported_format_of_last_msg += phone_number

        wt_exported_format_of_last_msg += ': '
        wt_exported_format_of_last_msg += message
        return wt_exported_format_of_last_msg

    def __getLastMsgFromPersonal(self, user_id):
        self.__cur.execute('SELECT user_id,group_id,date,message,message_status_id FROM MESSAGES WHERE group_id = ? AND user_id = ? ORDER BY date DESC LIMIT 1;', (0, user_id))
        details = self.__cur.fetchone()
        if details is None:
            return None

        user_id, group_id, date_time_string, message, message_status_id = details
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.strptime(date_time_string, format_in_db)

        date_time_string = (date_time_object.strftime(self.__whatsapp_time_format)).lower()
        if date_time_string[0] == '0' and self.__time_format == '12':
            date_time_string = date_time_string[1:]

        wt_exported_format_of_last_msg = '[' + date_time_string + '] '
        if int(message_status_id) == 0:
            wt_exported_format_of_last_msg += self.__user_name_of_wt_bot
        else:
            user_id, phone_number, user_name, is_saved_contact = self.__getUserDetailsInDBWithUserId(user_id)
            if int(is_saved_contact) == 1:
                wt_exported_format_of_last_msg += user_name
            else:
                wt_exported_format_of_last_msg += phone_number

        wt_exported_format_of_last_msg += ': '
        wt_exported_format_of_last_msg += message
        return wt_exported_format_of_last_msg

    def __closenessToPixel(self, rgb1, rgb2):
        return distance.euclidean(rgb1, rgb2)

    def __getUnreadChatFilterState(self):
        current_pixel_color = pag.pixel(self.__unread_chat_filter_coordinates[0], self.__unread_chat_filter_coordinates[1])
        closeness_to_filter_on = self.__closenessToPixel(current_pixel_color, self.__unread_chat_filter_on)
        closeness_to_filter_off = self.__closenessToPixel(current_pixel_color, self.__unread_chat_filter_off)
        if closeness_to_filter_on < closeness_to_filter_off:
            return "ON"
        else:
            return "OFF"

    def __turnOnUnreadChatFilter(self):
        if self.__getUnreadChatFilterState() == "OFF":
            pag.leftClick(self.__unread_chat_filter_coordinates[0], self.__unread_chat_filter_coordinates[1], self.__mouse_delay)
            time.sleep(2 * self.__delay)

    def __turnOffUnreadChatFilter(self):
        if self.__getUnreadChatFilterState() == "ON":
            pag.leftClick(self.__unread_chat_filter_coordinates[0], self.__unread_chat_filter_coordinates[1], self.__mouse_delay)
            time.sleep(2 * self.__delay)

    def newMessagesThere(self):
        current_pixel_color = pag.pixel(self.__whatsapp_coordinates[0], self.__whatsapp_coordinates[1])
        closeness_to_new_msg = self.__closenessToPixel(current_pixel_color, self.__whatsapp_new_msg)
        closeness_to_no_new_msg = self.__closenessToPixel(current_pixel_color, self.__whatsapp_no_new_msg)
        if closeness_to_new_msg < closeness_to_no_new_msg:
            return True
        return False

    def __insideSameChat(self, contact_info):
        if self.__current_open_chat == contact_info:
            return True
        if isinstance(contact_info, str):
            if isinstance(self.__current_open_chat, str):
                return False
            else:
                if self.__current_open_chat[0] == 'Group Chat':
                    if self.__current_open_chat[2] == contact_info:
                        return True
                    else:
                        return False
                if self.__current_open_chat[1] == 'Personal Chat':
                    if self.__current_open_chat[2] == contact_info or self.__current_open_chat[3] == contact_info:
                        return True
                    else:
                        return False
        if contact_info[0] == 'Group Chat':
            if contact_info[2] == self.__current_open_chat:
                return True
            else:
                return False
        if contact_info[1] == 'Personal Chat':
            if contact_info[2] == self.__current_open_chat or contact_info[3] == self.__current_open_chat:
                return True
            else:
                return False

    def lookForNewMessages(self):
        self.__openWhatsApp()
        self.__turnOffUnreadChatFilter()
        counter = 0
        while self.newMessagesThere() and counter<3:
            counter+=1
            self.__goToWhatsappDefaultState()
            self.__turnOnUnreadChatFilter()
            pag.leftClick(self.__first_chat_under_filter_coordinates[0], self.__first_chat_under_filter_coordinates[1], self.__mouse_delay)
            self.__turnOffUnreadChatFilter()
            scroll_length = 100
            contact_info = self.__getContactOrGroupInfo()

            copied_text = self.__selectAndCopyMessages(scroll_length)
            self.__current_open_chat = copy.deepcopy(contact_info)

            if contact_info[0] == 'Group Chat':
                group_id = contact_info[1]
                wt_exported_format_of_last_msg = self.__getLastMsgFromGrp(group_id)
            elif contact_info[0] == 'Personal Chat':
                user_id = contact_info[1]
                wt_exported_format_of_last_msg = self.__getLastMsgFromPersonal(user_id)
            if wt_exported_format_of_last_msg is None:
                last_msg_available_in_db = False
            else:
                index = (copied_text.lower()).find(wt_exported_format_of_last_msg.lower())
                if (index == -1):
                    last_msg_available_in_db = False
                else:
                    copied_text = copied_text[index + len(wt_exported_format_of_last_msg):]

            lines = copied_text.split('\n')
            intermediate_representation_msg = []
            if contact_info[0] == 'Group Chat':
                group_id = contact_info[1]
                group_name = contact_info[2]
                intermediate_representation_msg.append('Group Chat')
                intermediate_representation_msg.append(group_id)
                intermediate_representation_msg.append(group_name)
                intermediate_representation_msg.append([])

            if contact_info[0] == 'Personal Chat':
                user_id = contact_info[1]
                user_name = contact_info[2]
                phone_number = contact_info[3]
                intermediate_representation_msg.append('Personal Chat')
                intermediate_representation_msg.append(user_id)
                intermediate_representation_msg.append(user_name)
                intermediate_representation_msg.append(phone_number)
                intermediate_representation_msg.append([])

            if (self.__time_format == '12'):
                regex_msg_start = re.compile(
                    r"\[(1[0-2]:[0-5][0-9]|[1-9]:[0-5][0-9])\s(am|pm|AM|PM|Am|Pm), (\d\d/\d\d/\d\d\d\d|\d\d/\d\d\d\d/\d\d|\d\d\d\d/\d\d/\d\d)\] ([^:]+):\s([^\n]+)")
            elif (self.__time_format == '24'):
                regex_msg_start = re.compile(
                    r"\[(0[0-9]:[0-5][0-9]|1[0-9]:[0-5][0-9]|2[0-3]:[0-5][0-9]), (\d\d/\d\d/\d\d\d\d|\d\d/\d\d\d\d/\d\d|\d\d\d\d/\d\d/\d\d)\] ([^:]+):\s([^\n]+)")
            for i in range(len(lines)):
                matched = regex_msg_start.search(lines[i])
                if (matched is None) and (len(intermediate_representation_msg[-1]) != 0) and lines[i] != '':
                    intermediate_representation_msg[-1][-1][-1] = intermediate_representation_msg[-1][-1][-1] + '\n' + lines[i]

                if matched is not None:
                    if self.__time_format == '12':
                        time_ = matched.group(1)
                        period = matched.group(2)
                        date = matched.group(3)
                        date_time_string = time_ + ' ' + period + ', ' + date
                        ph_no_or_name = matched.group(4)
                        msg = matched.group(5)
                    else:
                        time_ = matched.group(1)
                        date = matched.group(2)
                        date_time_string = time_ + ', ' + date
                        ph_no_or_name = matched.group(3)
                        msg = matched.group(4)

                    if ph_no_or_name == self.__user_name_of_wt_bot:
                        intermediate_representation_msg[-1] = []
                        continue

                    date_time_object = datetime.strptime(date_time_string, self.__whatsapp_time_format)
                    format_in_db = '%Y-%m-%d %H:%M'
                    date_time_string = date_time_object.strftime(format_in_db)

                    current_msg_annotated = [date_time_object, date_time_string]
                    if intermediate_representation_msg[0] == 'Group Chat':
                        contact_info_of_user = self.__retrieveUserInfo(ph_no_or_name)
                        if contact_info_of_user is None:
                            self.__addUserInDb(phone_number=ph_no_or_name, user_name='', is_saved_contact=0)
                            contact_info_of_user = self.__getUserDetailsInDBWithPhone(ph_no_or_name)
                        current_msg_annotated.append(contact_info_of_user[0])
                        current_msg_annotated.append(contact_info_of_user[1])
                        current_msg_annotated.append(contact_info_of_user[2])

                    current_msg_annotated.append(msg)
                    intermediate_representation_msg[-1].append(current_msg_annotated)
            if len(intermediate_representation_msg[-1]) == 0:
                pass
            else:
                if intermediate_representation_msg[0] == 'Group Chat':
                    group_id = intermediate_representation_msg[1]
                    msg_status_id = 1
                    for z in range(len(intermediate_representation_msg[-1])):
                        date_time = intermediate_representation_msg[-1][z][1]
                        user_id = intermediate_representation_msg[-1][z][2]
                        msg = intermediate_representation_msg[-1][z][5]
                        self.__insertMessageWithoutCommit(user_id, group_id, date_time, msg, msg_status_id)
                        intermediate_representation_msg[-1][z].pop(0)
                        intermediate_representation_msg[-1][z].pop(1)
                    intermediate_representation_msg.pop(1)
                    self.__commitDBChanges()
                elif intermediate_representation_msg[0] == 'Personal Chat':
                    group_id = 0
                    user_id = intermediate_representation_msg[1]
                    msg_status_id = 1
                    for z in range(len(intermediate_representation_msg[-1])):
                        date_time = intermediate_representation_msg[-1][z][1]
                        msg = intermediate_representation_msg[-1][z][2]
                        self.__insertMessageWithoutCommit(user_id, group_id, date_time, msg, msg_status_id)
                        intermediate_representation_msg[-1][z].pop(0)
                    intermediate_representation_msg.pop(1)
                    self.__commitDBChanges()
                self.__new_messages.append(intermediate_representation_msg)
        self.__minimizeWhatsapp()

    def __goToTypeMessageBox(self):
        x = self.__type_message_coordinates[0]
        y = self.__type_message_coordinates[1]
        pag.leftClick(x, y, self.__mouse_delay)
        time.sleep(self.__delay)

    def sendText(self, ph_no_or_name, text):
        self.__openWhatsApp()
        self.__turnOffUnreadChatFilter()
        self.__openChat(ph_no_or_name)
        user_id = self.__getUserIdInDB(ph_no_or_name)
        if user_id is None:
            self.__getContactOrGroupInfo()
            user_id = self.__getUserIdInDB(ph_no_or_name)

            if user_id is None:
                self.__goToDefaultGroup()
                self.__minimizeWhatsapp()
                return
        self.__goToTypeMessageBox()
        self.__copyTextToClipBoard(text)
        self.__paste()
        pag.leftClick(self.__send_message_coordinates[0], self.__send_message_coordinates[1], self.__mouse_delay)
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.now()
        date_time_string = date_time_object.strftime(format_in_db)
        self.__insertMessageWithoutCommit(user_id, 0, date_time_string, text, 0)
        self.__commitDBChanges()
        self.goToProductivityGroup()
        self.__minimizeWhatsapp()

    def sendTextToGroup(self, group_name, text):
        self.__openWhatsApp()
        self.__turnOffUnreadChatFilter()
        self.__openChat(group_name)
        group_id = self.__getGroupIdInDB(group_name)
        if group_id is None:
            self.__getContactOrGroupInfo()

            group_id = self.__getGroupIdInDB(group_name)

            if group_id is None:
                self.__goToDefaultGroup()
                self.__minimizeWhatsapp()
                return
        self.__goToTypeMessageBox()
        self.__copyTextToClipBoard(text)
        self.__paste()
        pag.leftClick(self.__send_message_coordinates[0], self.__send_message_coordinates[1], self.__mouse_delay)
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.now()
        date_time_string = date_time_object.strftime(format_in_db)
        self.__insertMessageWithoutCommit(0, group_id, date_time_string, text, 0)
        self.__commitDBChanges()
        self.__minimizeWhatsapp()

    def __send_to_clipboard(self, image):
        output = BytesIO()
        image.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def sendImage(self, ph_no_or_name, img_location):
        self.__openWhatsApp()
        self.__turnOffUnreadChatFilter()
        self.__openChat(ph_no_or_name)
        user_id = self.__getUserIdInDB(ph_no_or_name)

        if user_id is None:
            self.__getContactOrGroupInfo()
            user_id = self.__getUserIdInDB(ph_no_or_name)

            if user_id is None:
                self.__goToDefaultGroup()
                self.__minimizeWhatsapp()
                return
        self.__goToTypeMessageBox()
        image = Image.open(img_location)
        self.__send_to_clipboard(image)
        pag.hotkey('ctrl', 'v')
        time.sleep(7 * self.__delay)
        pag.leftClick(self.__send_image_coordinates[0], self.__send_image_coordinates[1], self.__mouse_delay)
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.now()
        date_time_string = date_time_object.strftime(format_in_db)
        msg = 'Sent image at location:' + img_location
        self.__insertMessageWithoutCommit(user_id, 0, date_time_string, msg, 0)
        self.__commitDBChanges()
        self.goToProductivityGroup()
        self.__minimizeWhatsapp()

    def sendImageToGroup(self, group_name, img_location):
        self.__openWhatsApp()
        self.__turnOffUnreadChatFilter()
        self.__openChat(group_name)
        group_id = self.__getGroupIdInDB(group_name)
        if group_id is None:
            self.__getContactOrGroupInfo()
            group_id = self.__getGroupIdInDB(group_name)
            if group_id is None:
                self.__goToDefaultGroup()
                self.__minimizeWhatsapp()
                return
        self.__goToTypeMessageBox()
        image = Image.open(img_location)
        self.__send_to_clipboard(image)
        pag.hotkey('ctrl', 'v')
        time.sleep(7 * self.__delay)
        pag.leftClick(self.__send_image_coordinates[0], self.__send_image_coordinates[1], self.__mouse_delay)
        format_in_db = '%Y-%m-%d %H:%M'
        date_time_object = datetime.now()
        date_time_string = date_time_object.strftime(format_in_db)
        msg = 'Sent image at location:' + img_location
        self.__insertMessageWithoutCommit(0, group_id, date_time_string, msg, 0)
        self.__commitDBChanges()
        self.__minimizeWhatsapp()

    def getNewMessages(self):
        new_messages = copy.deepcopy(self.__new_messages)
        self.__new_messages = []
        return new_messages
