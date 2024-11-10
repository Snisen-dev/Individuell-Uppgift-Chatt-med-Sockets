import socket
import threading

nick = input("Välj ett smeknamn: ") #Smeknamn som andra klienter kommer se

HOST = "127.0.0.1"
PORT = 13370

# Anslut till servern och hantera eventuellt anslutningsfel
connected = False
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Skapa en TCP-socket
    sock.connect((HOST, PORT)) #Ansluter till servern
    connected = True #Om anslutningen lyckas ändras variabeln till sant
    print("Anslutning lyckades!")
except ConnectionRefusedError: #Om inte server kan nås
    print("Kunde inte ansluta till servern. Kontrollera att servern körs.") #Om endast "Client" körs kommer detta meddelande
    exit()

# Funktion för att ta emot meddelanden från servern
def receive():
    global connected #Tar in globala variabeln
    while connected:
        try:
            message = sock.recv(512).decode("utf-8")# Ta emot meddelande från servern
            if message == "NICK": #Om servern efterfrågar smeknamn
                sock.send(nick.encode("utf-8")) # Skicka smeknamn till servern
            else:
                print(message) #Skriver ut meddelande
        except ConnectionResetError: #Hanterar om servern kopplas ner
            print("Servern har stängt ner, du kopplas ifrån.")
            connected = False #Uppdaterar anslutningsstatus
            sock.close() #Stänger socketen
            break
        except OSError: #Hanterar fel när socketen redan är stängd
            break
        except Exception as e: #Fångar upp andra fel
            print(f"Ett fel uppstod: {e}")
            connected = False
            sock.close()
            break

#Funktion för att kunna skicka meddelande till servern
def write():
    global connected
    while connected:
        message = input("") 
        if message.lower() == "exit": #Om användaren vill lämna chatten
            try:
                sock.send("exit".encode("utf-8")) #Skickar "exit" till servern
                print("Du har lämnat chatten.")
            except (BrokenPipeError, OSError): #felhantering
                print("Kunde inte skicka meddelandet, anslutningen är stängd.")
            finally:
                connected = False
                sock.close()
                break
        else:
            full_message = f"{nick}: {message}" #Skapar kompletta meddelandet med smeknamnet
            try:
                sock.send(full_message.encode("utf-8"))
            except (BrokenPipeError, OSError): #Hanterar feldata om anslutningen är förlorad
                print("Anslutningen till servern är förlorad.")
                connected = False
                sock.close()
                break

# Starta trådar för skicka och ta emot meddelanden
if connected:
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()
