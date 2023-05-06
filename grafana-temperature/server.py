import machine
import utime
import network
import socket as sockImport
import time
# Configuration
SSID = ''
WIFI_PASSWORD = ''
WEB_SERVER_PORT = 8080
led= machine.Pin("LED", machine.Pin.OUT)


sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535) #used to convert reading to voltage
# Connect to wifi
 

def connect_wlan():
    sta_if = network.WLAN(network.STA_IF) #connects to a router
    print("is connected "+str(sta_if.isconnected()))

    print("Connecting")
    sta_if.active(True)
    sta_if.connect(SSID, WIFI_PASSWORD)
    max_wait = 10
    while max_wait>0:
        if sta_if.status()<0 or sta_if.status()>=3:
            break
        time.sleep(1)
        max_wait-=1
    if (sta_if.status()!=3):
        print("Failed to connect to wifi")
    else:
        print("Connected. Config:",sta_if.ifconfig()[0]) #tuple of address, subnet, router address and dns
        #what is return type of ifconfig?
        
def get_temperature():
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    print("temperature: "+str(temperature))
    return temperature

def start_server():
    addr = sockImport.getaddrinfo('0.0.0.0',WEB_SERVER_PORT)[0][-1]
    sock = sockImport.socket(sockImport.AF_INET, sockImport.SOCK_STREAM) #INET is address family for ipv4 and sock stream is tcp socket type
    sock.bind(addr)
    sock.listen(1)
    print("listening on", addr)
    while True:
        try:
            cl, addr = sock.accept()
            print("client connected from", addr)
            
            request = cl.recv(1024) 
            print(request)#is discarded
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')  #this is status and header          
            #cl.send('# HELP pico temp')
            #cl.send('# TYPE pico_temperature gauge\n')
            cl.send("pico_temperature {}".format(get_temperature()))
            cl.close() #closes connection after each request
        except OSError as e:
            cl.close()
            print("Connection closed with exception:", e)



print("Starting")
connect_wlan() 
led.value(1)
time.sleep(1)
led.value(0)
start_server()
