import pyautogui as pag

class WhatsappBot:
    def __init__(self, setup_name):
        self.__whatsapp_path = None
        self.__wt_version = None
        self.__whatsapp_coordinates = None
        self.__whatsapp_new_msg = None
        self.__whatsapp_no_new_msg = None
        self.__unread_chat_filter_coordinates = None
        self.__unread_chat_filter_on = None
        self.__unread_chat_filter_off = None
        self.__kebab_menu_coordinates = None
        self.__contact_info_coordinates = None
        self.__contact_info_field1_coordinates = None
        self.__contact_info_field2_coordinates = None
        self.__contact_info_field2_coordinates_for_group = None
        self.__contact_info_field2_coordinates_for_unsaved = None
        self.__close_contact_info_coordinates = None
        self.__latest_message_coordinates = None
        self.__copy_latest_message_coordinates = None
        self.__type_message_coordinates = None
        self.__first_chat_under_filter_coordinates = None
        self.__second_chat_under_filter_coordinates = None
        self.__minimize_whatsapp_coordinates = None
        self.__show_desktop_coordinates = None
        self.__top_left_in_chat = None
        self.__bottom_right_in_chat = None
        self.__user_name_of_wt_bot = None
        self.__default_group = None
        self.__send_message_coordinates = None
        self.__send_image_coordinates = None
        self.__search_bar_coordinates = None
        self.__kebab_menu_for_filter_coordinates = None
        self.__filter_by_coordinates = None
        self.__unread_coordinates = None
        self.__close_filter_coordinates = None
        self.__whatsapp_time_format = None
        self.__time_format = '12' if '%p' in self.__whatsapp_time_format else '24'
        self.__width = pag.size()[0]
        self.__height = pag.size()[1]
        self.__delay = 1.0
        self.__mouse_delay = 0.5
        self.__type_delay = 0.1