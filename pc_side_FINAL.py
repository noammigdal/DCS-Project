import PySimpleGUI as sg
import serial as ser
import sys, glob
import time
import serial.tools.list_ports
from tkinter import *
from tkinter.colorchooser import askcolor
import mouse
import os
from os import path
import threading
import binascii
import pyautogui


class Paint(object):
    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'Black'

    def __init__(self):
        self.root = Tk()

        self.pen_button = Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.brush_button = Button(self.root, text='Back', command=self.close_painter)
        self.brush_button.grid(row=0, column=1)

        self.color_button = Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=2)

        self.eraser_button = Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=3)

        self.choose_size_button = Scale(self.root, from_=6, to=10, orient=HORIZONTAL)

        self.choose_size_button.grid(row=0, column=4)

        self.c = Canvas(self.root, bg='white', width=600, height=600)
        self.c.grid(row=1, columnspan=5)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<Motion>', self.paint)
        # self.c.bind('<ButtonRelease-1>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_brush(self):
        self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        global state
        if state == 0 and self.old_x and self.old_y:  # paint
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=self.color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        elif state == 1 and self.old_x and self.old_y:  # erase
            # paint_color = 'white'
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill='white',
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        elif state == 2:  # Neutral
            pass
        else:
            pass

        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def close_painter(self):

        global paint_in_progress
        paint_in_progress = 0
        self.root.destroy()


class PortError(Exception):

    pass


# Automatic PORT search
#def port_search(between=None):
    # find the right com that connect between the pc and controller
   # ports = serial.tools.list_ports.comports()
   # for desc in sorted(ports):
    #    if "MSP430" in desc.description:
     #       return desc.device
   # raise PortError


def show_window(layout_num, window):
    for i in range(1, 7):
        if i == layout_num:
            window[f'COL{layout_num}'].update(visible=True)
        else:
            window[f'COL{i}'].update(visible=False)


def send_state(message=None, file_option=False):
    s.reset_output_buffer()
    if file_option:
        bytesMenu = message
    else:
        bytesMenu = bytes(message, 'ascii')
    s.write(bytesMenu)


def read_MSP_Data(state, size):
    n = 4
    while True:
        while s.in_waiting > 0:  # while the input buffer isn't empty
            if state == 'Painter':
                message = s.read(size=size)  # at Painter size = 6
                message = binascii.hexlify(message).decode('utf-8')
                message_split = "".join([message[x:x + 2] for x in range(0, len(message), 2)][::-1])
                final_message = [message_split[i:i + n] for i in range(0, len(message_split), n)]
            elif state == 'script':

                final_message = s.read(size=size).decode('utf-8')  # at Painter size = 4

            else:
                final_message = s.readline().decode('utf-8')

            return final_message



def get_joystick_params():
    global state
    param = read_MSP_Data('Painter', 4)
    Vx = int((param[0]), 16)
    Vy = int((param[1]), 16)
    if Vx > 1024 or Vy > 1024:
        param[0] = "".join([param[0][x:x + 2] for x in range(0, len(param[0]), 2)][::-1])
        param[1] = "".join([param[1][x:x + 2] for x in range(0, len(param[1]), 2)][::-1])
        Vx = int((param[0]), 16)
        Vy = int((param[1]), 16)

    print("Vx: " + str(Vx) + ", Vy: " + str(Vy) + ", state: " + str(state))


    return Vx, Vy


#def message_handler(message=None, FSM=False, file=False):
 #   s.reset_output_buffer()
  #  txChar = message  # enter key to transmit
   # if FSM:
    #    s.write(b"\x7f")
   # if not file:
   #     bytesChar = bytes(txChar, 'ascii')
   # else:
    #    bytesChar = txChar
   # s.write(bytesChar)
   # print(f"cp send: {message}")


def start_painter(window):
    Paint()

global file_to_run
file_to_run = ""

def GUI():
    global file_to_run
    global run_state
    run_state = ''

    sg.theme('Black2')

    layout_main = [
        [sg.Text("DCS Final Project - Nitzan and Noam", size=(35, 3), justification='center', font='Verdana 15')],
        [sg.Button("Motor Manual control", key='_Manual_', size=(35, 4), font='Verdana 15')],
        [sg.Button("Painter using joystick", key='_Painter_', size=(35, 4), font='Verdana 15')],
        [sg.Button("Calibration", key='_Calibration_', size=(35, 4), font='Verdana 15')],
        [sg.Button("Script", key='_Script_', size=(35, 4), font='Verdana 15')]
    ]

    layout_manual = [
        [sg.Text("Motor Manual control", size=(35, 2), justification='center', font='Verdana 15')],
        [sg.Button("Rotate", key='_Rotation_', size=(10, 1), font='Verdana 15'),
         sg.Button("Stop", key='_Stop_', size=(10, 1), font='Verdana 15'),
         sg.Button("JoyStick", key='_JoyStick_', size=(10, 1), font='Verdana 15')],
        [sg.Button("Back", key='_BackMenu_', size=(5, 1), font='Verdana 15', pad=(300, 180))]
    ]

    layout_painter = [
        [sg.Text("Painter using joystick", size=(35, 2), justification='center', font='Verdana 15')],
        [sg.Canvas(size=(100, 100), background_color='red', key='canvas')],
        [sg.Button("Back", key='_BackMenu_', size=(5, 1), font='Verdana 15', pad=(300, 180))]
    ]

    layout_calibration = [
        [sg.Text("Calibration", size=(35, 2), justification='center', font='Verdana 15')],
        [sg.Button("Start", key='_Rotation_', size=(18, 1), font='Verdana 15'),
         sg.Button("Stop", key='_Stop_', size=(18, 1), font='Verdana 15')],
        [sg.Text("Counter: ", justification='center', font='Verdana 15'),
         sg.Text(" ", size=(35, 2), key="Counter", justification='center', font='Verdana 15')],
        [sg.Text("deg: ", justification='center', font='Verdana 15'),
         sg.Text(" ", size=(35, 2), key="deg", justification='center', font='Verdana 15')],
        [sg.Button("Back", key='_BackMenu_', size=(5, 1), font='Verdana 15')]
    ]

    file_viewer = [[sg.Text("File Folder"),
                    sg.In(size=(30, 1), enable_events=True, key='_Folder_'),
                    sg.FolderBrowse()],
                   [sg.Listbox(values=[], enable_events=True, size=(50, 23), key="_FileList_")],
                   [sg.Button('Back', key='_BackMenu_', size=(8, 1), font='Verdana 15'),
                    sg.Button('Download', key='_Download_', size=(8, 1), font='Verdana 15')],
                    [sg.Text(' ', key='_ACK_', size=(50, 1), font='Verdana 10')]]

    file_description = [
        [sg.Text("File Description", size=(45, 1), justification='center', font='Verdana 15')],
        [sg.Text(size=(45, 1), key="_FileHeader_", font='Verdana 11')],
        [sg.Multiline(size=(45, 15), key="_FileContent_")],
        [sg.HSeparator()],
        [sg.Text("MSP Files", size=(45, 1), justification='center', font='Verdana 15')],
        [sg.Listbox(values=[], enable_events=True, size=(45, 4), key="_ExecutedList_")],
        [sg.Button('Execute', key='_Execute_', size=(20, 1), font='Verdana 15'),
        sg.Button('Clear', key='_Clear_', size=(20, 1), font='Verdana 15')]
    ]

    layout_calc = [
        [sg.Text(" ", key='_FileName_', size=(35, 2), justification='center', font='Verdana 15')],
        [sg.Text("Current Degree: ", justification='center', font='Verdana 15'),
         sg.Text(" ", size=(35, 2), key="Degree", justification='center', font='Verdana 15')],
        [sg.Button("Back", key='_BackScript_', size=(5, 1), font='Verdana 15')],
        [sg.Button('Run', key='_Run_', size=(38, 1), font='Verdana 15')]
    ]

    layout_script = [[sg.Column(file_viewer),
                      sg.VSeparator(),
                      sg.Column(file_description)]]

    layout = [[sg.Column(layout_main, key='COL1', ),
               sg.Column(layout_manual, key='COL2', visible=False),
               sg.Column(layout_painter, key='COL3', visible=False),
               sg.Column(layout_calibration, key='COL4', visible=False),
               sg.Column(layout_script, key='COL5', visible=False),
               sg.Column(layout_calc, key='COL6', visible=False)]]

    global window
    # Create the Window
    window = sg.Window(title='Control System of motor-based machine', element_justification='c', layout=layout,
                       size=(1000, 900))
    canvas = window['canvas']
    execute_list = []
    empty_list = []
    file_name = ''
    file_size = ''
    file_path = ''
    global paint_in_progress
    while True:
        event, values = window.read()
        if event == "_Manual_":
            send_state('m')
            show_window(2, window)
            while "_BackMenu_" not in event:
                event, values = window.read()
                if event == "_Rotation_":
                    send_state('A')
                elif event == "_Stop_":
                    send_state('M')
                elif event == "_JoyStick_":
                    send_state('J')

        if event == "_Painter_":
            global state
            paint_in_progress = 1
            send_state('P')
            paint_thread = threading.Thread(target=start_painter, args=(window,))
            paint_thread.start()
            firstTime = 1
            while paint_in_progress:
                try:
                    Vx, Vy = get_joystick_params()
                except:
                    continue
                if Vx == 1000 and Vy == 1000:
                    state = (state + 1) % 3
                if (Vy > 650 and Vy < 750) and (Vx >650 and Vx < 750):
                    state = state
                elif firstTime:
                    x_init, y_init = Vx, Vy
                    firstTime = 0
                else:
                    dx, dy = Vx, Vy
                    new_x, new_y = mouse.get_position()
                    dx, dy = int(dx) - int(x_init), int(dy) - int(y_init)
                    mouse.move(new_x - int(dx / 50), new_y - int(dy / 50))
            show_window(1, window)

        if event == "_Calibration_":
            send_state('C')
            show_window(4, window)
            while "_BackMenu_" not in event:
                event, values = window.read()
                if "_Rotation_" in event:
                    send_state('A')
                elif "_Stop_" in event:
                    send_state('M')
                    counter = read_MSP_Data('calib', 4)
                    counter += '0'
                    print(counter)
                    window["Counter"].update(value=counter)
                    print(counter.split('\x000')[0])
                    phi = 360 / int(counter.split('\x000')[0])
                    window["deg"].update(value=str(round(phi, 4)) + "[deg]")

        if event == "_Script_":
            burn_index = 0
            send_state('s')
            show_window(5, window)

        if event == '_Folder_':
            selected_folder = values['_Folder_']
            try:
                window["_FileContent_"].update('')
                window["_FileHeader_"].update('')
                file_path = ''
                file_list = os.listdir(selected_folder)
            except Exception as e:
                file_list = []
            fnames = [f for f in file_list if
                      os.path.isfile(os.path.join(selected_folder, f)) and f.lower().endswith(".txt")]
            window["_FileList_"].update(fnames)

        if event == '_FileList_':
            try:
                file_path = os.path.join(values["_Folder_"], values["_FileList_"][0])
                file_size = path.getsize(file_path)
                try:
                    with open(file_path, "rt", encoding='utf-8') as f:
                        file_content = f.read()
                except Exception as e:
                    print("Error: ", e)
                file_name = values["_FileList_"][0]
                window["_FileHeader_"].update(f"File name: {file_name} | Size: {file_size} Bytes")
                window["_FileContent_"].update(file_content)
            except Exception as e:
                print("Error: ", e)
                window["_FileContent_"].update('')

        if event == '_Download_':
            send_state(f"{file_name}\n")
            execute_list.append(f"{file_name}")
            time.sleep(0.1)
            time.sleep(0.1)
            try:
                with open(file_path, "rb") as f:
                    file_content_b = f.read()
            except Exception as e:
                print("Error: ", e)
            send_state(file_content_b + bytes('Z', 'utf-8'), file_option=True)
            print(file_name)
            print(f"{file_size}")
            time.sleep(0.5)
            if (burn_index == 0):
                ptr_state = 'W'
            elif (burn_index == 1):
                ptr_state = 'X'
            elif (burn_index == 2):
                ptr_state = 'Y'
            burn_index += 1
            send_state(ptr_state)
            try:
                burn_ack = read_MSP_Data('script', 3).rstrip('\x00')
            except:
                print("error")
            if burn_ack == "FIN":
                window['_ACK_'].update('"'+file_name+'"'+' downloaded successfully!')
                window.refresh()
                print(burn_ack)
            print("burn file index: " + ptr_state)
            time.sleep(0.3)
            window['_ExecutedList_'].update(execute_list)

        if event == '_ExecutedList_':
            if values["_ExecutedList_"]:
                file_to_run = values["_ExecutedList_"][0]
                print(f"Selected file to execute: {file_to_run}")
            file_index = execute_list.index(file_to_run)
            if (file_index == 0):
                run_state = 'T'
            elif (file_index == 1):
                run_state = 'U'
            elif (file_index == 2):
                run_state = 'V'

        if event == '_Execute_':
            if file_to_run != "":
                new_phi = 0
                step_deg = 360 / 514
                show_window(6, window)
                window['_FileName_'].update('"' + file_to_run + '"' + " execute window")
                while "_BackScript_" not in event:
                    event, values = window.read()
                    if event == '_Run_':
                        time.sleep(0.5)
                        send_state(run_state)
                        print("execute file index: " + run_state)
                        time.sleep(0.6)
                        s.reset_input_buffer()
                        s.reset_output_buffer()
                        new_counter = read_MSP_Data('script', 3).rstrip('\x00')
                        print(new_counter)
                        while new_counter != "FIN":
                            while 'F' not in new_counter:
                                window.refresh()
                                new_phi = int(new_counter) * step_deg
                                window["Degree"].update(value=str(round(new_phi, 4)) + "[deg]")
                                new_counter = read_MSP_Data('script', 3).rstrip('\x00')
                                print(new_counter)
                            new_counter = read_MSP_Data('script', 3).rstrip('\x00')
                            print(new_counter)
                            window.refresh()
                            if 'F' not in new_counter:
                                new_phi = int(new_counter) * step_deg
                                window["Degree"].update(value=str(round(new_phi, 4)) + "[deg]")
                        window.refresh()
            else:
                sg.popup("Please select a file first.")

        if event == '_Clear_':
            window['_ExecutedList_'].update(empty_list)
            window['_ACK_'].update(' ')

        if event == sg.WIN_CLOSED:
            break

        if event is not None and "_BackMenu_" in event:
            show_window(1, window)
        if event is not None and "_BackScript_" in event:
            show_window(5, window)
    window.close()


if __name__ == '__main__':

    s = ser.Serial('COM3', baudrate=9600, bytesize=ser.EIGHTBITS,
                   parity=ser.PARITY_NONE, stopbits=ser.STOPBITS_ONE,
                   timeout=1)
    s.flush()  # clear the port
    enableTX = True
    s.set_buffer_size(1024, 1024)
    s.reset_input_buffer()
    s.reset_output_buffer()
    firstTime = 1

    state = 2  # neutral state

    paint_in_progress = 0

    GUI()