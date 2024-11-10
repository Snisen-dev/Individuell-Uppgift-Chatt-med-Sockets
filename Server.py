import socket
import threading #threading används för att göra det möjligt att hantera flera klienter

HOST = "127.0.0.1" #lokalhost
PORT = 13370 #Inte mindre än 1024 och gärna ett 5 siffrigt tal

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #skapar en TCP-server
sock.bind((HOST, PORT)) #Binder servern till HOST, PORT
sock.listen() #Servern börjar lyssna på inkommande anslutningar

#mypy vill att man ska definiera tomma variabler
clients:list = [] #lista för klienterna
nicks:list = [] #lista för smeknamn
server_running = True #En koll om Servern körs eller inte

# Funktion för att skicka meddelanden till alla anslutna klienter
def broadcast(message):
    if not server_running:  # Om servern inte körs, skicka inga meddelanden
        return
    for client in clients[:]:  # Skapar en kopia av listan för att kunna ta bort säkert
        try:
            client.send(message.encode("utf-8"))  # Skicka meddelandet till klienten
        except (BrokenPipeError, ConnectionAbortedError, OSError):  # Hantera fel om klienten kopplar ner
            clients.remove(client)  # Ta bort klienten från listan
            print("En klient kopplades bort oväntat och har tagits bort.")

#Funktion för att hantera enskilda klienter
def handle(client):
    while True:
        try:
            message = client.recv(512).decode("utf-8")  # Tar emot och avkodar meddelandet från klienten
            index = clients.index(client)  # Hämta klientens index 
            nick = nicks[index]  # Hämta smeknamnet för klienten
            
            if message == "exit":  # Om klienten skickar "exit", hantera utloggning
                broadcast(f"{nick} har lämnat chatten.")  # Informera andra klienter
                clients.pop(index)  # Ta bort klienten från listan
                nicks.pop(index)  # Ta bort smeknamnet från listan
                break 
            else:
                broadcast(message)  # Skicka meddelandet till alla klienter
        except:  # Hantera fel (t.ex. om klienten kopplar ner oväntat)
            if client in clients:
                broadcast(f"{nick} lämnade chatten.")
                clients.pop(index)  
                nicks.pop(index) 
            break  

    client.close()  # Stäng klientens socketanslutning

def receive():
    while server_running:
        try:
            client, address = sock.accept() # Acceptera ny klientanslutning
            print(f"Klient ansluten med {str(address)}")
            #Skickar "NICK"-begäran till Klienten första gången den ansluter
            client.send("NICK".encode("utf-8"))
            nick = client.recv(512).decode("utf-8") #Tar emot nick ifrån Klienten 
            nicks.append(nick) #Lägger till det i listan nicks
            clients.append(client) #Lägger till klienten i listan

            broadcast(f"{nick} har anslutit till chatten") 
            client.send("Du har anslutit till chatten".encode("utf-8")) 
            
            # Skapa en ny tråd för att hantera denna klient
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except OSError:
            # Detta hanterar fel som uppstår när socketen stängs ner med "Exit"
            break

#Funktion för att stänga ner servern
def listen_for_server_exit():
    global server_running
    while server_running:
        command = input("")
        if command.lower() == "exit": # Vänta på att användaren skriver "exit"
            print("Servern stängs ner...")
            server_running = False 
            broadcast("Servern har stängts ner.")
            for client in clients: # Stänger alla anslutningar
                client.close()
            sock.close() # Stäng serverns socket
            break

print("Servern är uppe")
receive_thread = threading.Thread(target=receive) # Starta "tråd" för att hantera anslutningar
receive_thread.start()

exit_thread = threading.Thread(target=listen_for_server_exit) # Starta "tråd" för att hantera servernedstängning
exit_thread.start()
