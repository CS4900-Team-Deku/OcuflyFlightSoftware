# This example script demonstrates how use Python to allow users to send SDK to Tello commands with their keyboard
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/

# Import the necessary modules
import socket
import threading
import time
import sys
from tkinter import Tk, Button, Label, Scale

# IP and port of Tello
tello_address = ('192.168.10.1', 8889)

# IP and port of local computer
local_address = ('', 9000)

# Create a UDP connection that we'll send the command to
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the local address and port
sock.bind(local_address)

# Button Commands
default_speed = 30
default_yaw = 30

def command_button_click():
    send("command")
    
def takeoff_button_click():
    send("takeoff")

def land_button_click():
    send("land")

def battery_button_click():
    send("battery?")

def end_button_click():
    send("land")
    sys.exit(0)

def move_forward(event):
    send("rc 0 " + str(speed_slider.get()) + " 0 0")
    
def move_left(event):
    send("rc -" + str(speed_slider.get()) +  " 0 0 0")

def move_right(event):
    send("rc " + str(speed_slider.get()) + " 0 0 0")

def move_back(event):
    send("rc 0 -" + str(speed_slider.get()) + " 0 0")

def stop(event):
    send("rc 0 0 0 0")

def move_up(event):
    send("up " + str(speed_slider.get()))

def move_down(event):
    send("down " + str(speed_slider.get()))

def rotate_cw(event):
    send("cw " + str(rotation_slider.get()))
    if rotation_slider.get()>180:
        rotation_slider.set(default_yaw)

def rotate_ccw(event):
    send("ccw " + str(rotation_slider.get()))
    if rotation_slider.get()>180:
        rotation_slider.set(default_yaw)

def speed_increase(event):
    speed = speed_slider.get()
    if speed > 90:
        speed_slider.set(100)
    else:
        speed = speed + 10
        speed_slider.set(speed)

def speed_decrease(event):
    speed = speed_slider.get()
    if speed < 10:
        speed_slider.set(0)
    else:
        speed = speed - 10
        speed_slider.set(speed)
    

# Send the message to Tello and allow for a delay in seconds
def send(message):
    # Try to send the message otherwise print the exception
    try:
        sock.sendto(message.encode(), tello_address)
        print("Sending message: " + message)
    except Exception as e:
        print("Error sending: " + str(e))

# Receive the message from Tello
def receive():
    # Continuously loop and listen for incoming messages
    while True:
    # Try to receive the message otherwise print the exception
        try:
            response, ip_address = sock.recvfrom(128)
            print("Received message: " + response.decode(encoding='utf-8'))
#            incoming_label.config(text = "\n\nReceived message: " + response.decode(encoding='utf-8'))
        except Exception as e:
            # If there's an error close the socket and break out of the loop
            sock.close()
            print("Error receiving: " + str(e))
            break

def battery_percentage():
    send("battery?")
    while True:
        try:
            response, ip_address = sock.recvfrom(128)
            battery_label.config(text = "Battery: " + response.decode(encoding='utf-8') + "%")
        except Exception as e:
            sock.close()
            break

# Create and start a listening thread that runs in the background
# This utilizes our receive function and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

# Loop infinitely waiting for commands or until the user types quit or ctrl-c
while True:
    flight_application = Tk()
    flight_application.title("Ocufly")
    buttonWidth = 10

    command_button = Button(flight_application,
                            text = "Connect",
                            command = command_button_click,
                            width = buttonWidth)
    command_button.grid(row = 0, column = 0)

    takeoff_button = Button(flight_application,
                            text = "Takeoff",
                            command = takeoff_button_click,
                            width = buttonWidth)
    takeoff_button.grid(row = 1, column = 0)

    land_button = Button(flight_application,
                         text = "Land",
                         command = land_button_click,
                         width = buttonWidth)
    land_button.grid(row = 2, column = 0)

    battery_button = Button(flight_application,
                            text = "Battery Level",
                            command = battery_button_click,
                            width = buttonWidth)
    battery_button.grid(row = 3, column = 0)

    end_button = Button(flight_application,
                        text = "End",
                        command = end_button_click,
                        width = buttonWidth)
    end_button.grid(row = 4, column = 0, )
    
    incoming_label = Label(flight_application, text = "\n\nClick Connect")
    incoming_label.grid(row = 5, column = 0)

    speed_slider_label = Label(flight_application, text = "\n\nSpeed")
    speed_slider_label.grid(row = 6, column = 0)
    speed_slider = Scale(flight_application,
                            orient = "horizontal",
                            from_= 0, to = 100)
    speed_slider.set(default_speed)
    speed_slider.grid(row = 7, column = 0)

    rotation_slider_label = Label(flight_application, text = "\n\nDegrees of rotation")
    rotation_slider_label.grid(row = 8, column = 0)
    rotation_slider = Scale(flight_application,
                            orient = "horizontal",
                            from_= 1, to = 360,)
    rotation_slider.set(default_yaw)
    rotation_slider.grid(row = 9, column = 0)
    
    controls_label = Label(flight_application, text = "\n\nWASD controls\nArrow keys altitude/yaw\n=/- change speed")
    controls_label.grid(row = 10, column = 0)
    
    battery_label = Label(flight_application, text = "N/A")
    battery_label.grid(row = 11, column = 0)

    flight_application.bind('w', move_forward)
    flight_application.bind('a', move_left)
    flight_application.bind('s', move_back)
    flight_application.bind('d', move_right)
    flight_application.bind('<Up>', move_up)
    flight_application.bind('<Down>', move_down)
    flight_application.bind('<Left>', rotate_ccw)
    flight_application.bind('<Right>', rotate_cw)
    flight_application.bind('<space>', stop)
    flight_application.bind('=', speed_increase)
    flight_application.bind('-', speed_decrease)
    
    flight_application.mainloop()

    try:
        # Read keybord input from the user
        if(sys.version_info > (3, 0)):
            # Python 3 compatibility
            message = input('')
        else:
            # Python 2 compatibility
            message = raw_input('')

        # If user types quit then lets exit and close the socket
        if 'quit' in message:
            print("Program exited sucessfully")
            sock.close()
            break

        # Send the command to Tello
        send(message)

    # Handle ctrl-c case to quit and close the socket
    except KeyboardInterrupt as e:
        sock.close()
        break