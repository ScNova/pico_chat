#AI used to undertstand how threading works, to divide tasks and to prevent the use of uart.write at the same time 
import _thread
import time
from machine import UART , Pin

time.sleep(0.1)

#uart connection to pico 2
uart = UART(1 , baudrate = 9600 , tx = Pin(8) , rx = Pin(9), timeout=50)

#using this variable to check when the last time the message was sent either by send_message or wait_message
last_sent = time.ticks_ms()

#thread lock method to give priority 
uart_lock = _thread.allocate_lock()

#to avoid user_message and waiting_message sending at the same time
def send_message(message):
    """get a message from user_message or wait_message and send it"""
    global last_sent
    
    #give priority to one thread at a time 
    with uart_lock:
        uart.write((message + "\n").encode())
        last_sent= time.ticks_ms()
    
#----Receive messages and send a maintien de connexion with time----

def read_wait_message():
    """check for a message sent by the other pico and also Check if the user has sent a message in the last 10 sec if not send a message to the other pico """
    
    while True:

        #----read----

        recu = uart.readline()
        if recu :
            print("pico1: ", recu.decode().strip())

        #----Send a message if the user has not sent one after 10 sec----

        # check when the last message was sent to pico 2 
        elapsed_time = time.ticks_diff(time.ticks_ms(),last_sent)
        if elapsed_time > 10000:
            now = time.localtime()
            message  = ("maintien de connexion " + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]))
            send_message(message)
        time.sleep_ms(50)

#----Start the thread----

_thread.start_new_thread(read_wait_message, ())
  

while True:

    #----Get user input----
    
    message = input("Entrer un message: ")
    send_message(message)
    time.sleep(2)


