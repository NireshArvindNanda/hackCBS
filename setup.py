from tkinter import *
from pynput import mouse
import pyautogui as pag


class setup:
    def __init__(self):
        self.__label_for_coordinates = None
        self.__label_for_color = None
        self.__root = None
        self.__listener = None
        self.__welcomeScreen()

    def __on_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            if pressed:
                if self.__label_for_coordinates is not None:
                    position = pag.position()
                    self.__label_for_coordinates['text'] = str(position)

                if self.__label_for_color is not None:
                    pixel = pag.pixel(x, y)
                    self.__label_for_color['text'] = str(pixel)

    def __welcomeScreen(self):
        self.__root = Tk()
        self.__listener = mouse.Listener(on_click=self.__on_click)
        self.__listener.start()
        self.__root.geometry("700x350")
        self.__root.attributes('-topmost', True)
        Label(self.__root, text="These are the x,y coordinates for kebab menu",fg='blue').grid(row=0, column=0)
        self.__label_for_coordinates = Label(
            self.__root, text='Right click over point')
        self.__label_for_coordinates.grid(row=0, column=1)

        self.__label_for_color = Label(
            self.__root, text='Right click over point')
        self.__label_for_color.grid(row=2, column=1)
        next_button = Button(self.__root, text='Next',
                             command=self.__on_click,width=10,bg='red',fg='white')
        next_button.grid(row=3, column=0,pady=15)

        Label(self.__root,text="This is the color value in RGB",fg='blue').grid(row=2,column=0)

        self.__root.mainloop()

setup()