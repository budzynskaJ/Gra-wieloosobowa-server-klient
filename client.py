# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 16:04:34 2021

@author: aleks
"""

"""Gra wieloosobowa - podaj liczbe najblizsza sredniej

Zasady gry opisane zostały w pliku server.py.

Aby poprawnie zaczac gre, nalezy uruchomic plik serwera server.py oraz co najmniej
4 pliki klienta/gracza client.py (w przypadku gdy uruchomiona zostanie mniej plikow
lub zadnen plik client.py, gra sie nie rozpocznie i zostanie wyslana wiadomosc
o zbyt malej ilosci graczy). 
Pliki mozna uruchomic albo w terminalu komputera, albo w srodowisku programistycznym
odpowiednim dla pythona.

To jest plik obsługiwany przez klientów (graczy).
"""

import socket

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostbyname(socket.gethostname())
port = 5050

connected = True

tekst = """Witamy w grze!!! Jest to gra wieloosobowa, minimalna liczba graczy 
wynosi 4. Gracze maja 45s na dolaczenie do gry. Gra polega na wymysleniu liczby z przedziału (0, 20>. Turę wygrywa
osoba, która wymysli liczbę najbliższą sredniej. Jeżeli kilku graczy wymysli
taką samą liczbę najbliższą sredniej - tracą oni po punkcie. Gra kończy się gdy
jeden z graczy zdobędzie 3 punkty.\n """

print(tekst)

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

        
"""Fragment 1
Fragment kodu obslugujacy wczytywanie nicku wpisywanego przez graczy oraz 
wysylanie go do serwera
Obsluguje on rowniez sytuacje, w której bedzie za malo chetnych do gry. Klienci
dostaja wtedy wiadomosc z informacja, ze gra nie moze sie rozpoczac i zamykane
sa ich konsole.
"""

tmp = True
m = ClientSocket.recv(1024)
print(m.decode('utf-8'))
       
my_username = input()
if len(my_username) > 0:    
    ClientSocket.send(my_username.encode('utf-8'))
else:
    ClientSocket.send(' '.encode('utf-8'))
            
while tmp:
        
    message1 = ClientSocket.recv(1024).decode('utf-8')
          
    if message1 == "Nieprawidłowy nick. Podaj swój nick jeszcze raz:":
        print(message1)
        my_username = input()
        if len(my_username) > 0:
            ClientSocket.send(my_username.encode('utf-8'))
        else: 
            ClientSocket.send(' '. encode('utf-8'))
    elif message1 == "Ten nick jest już zajęty. Podaj inny nick: ":
        print(message1)
        my_username = input()
        ClientSocket.send(my_username.encode('utf-8'))
    else:
        print(message1)
        tmp = False
     
starting = ClientSocket.recv(1024).decode('utf-8')
if starting == 'koniec':
    print("Niestety za mało graczy dolaczylo, by rozpoczac gre")
    ClientSocket.close()
    tmp = False
else:
    print(starting)
    tmp = True

"""Koniec Fragmentu 1
"""
   


"""Fragment 2
Fragment kodu obsługujący wpisywanie przez graczy liczb i wyboru kontynuacji
gry w przypadku jej zakonczenia oraz wysylanie informacji do serwera
"""

while tmp:
       message2 = ClientSocket.recv(1024).decode('utf-8')
       if message2 == 'ok':
           scoring = ClientSocket.recv(1024).decode('utf-8')
           maximal = ClientSocket.recv(1024).decode('utf-8')
           print(scoring)
                    
           if int(maximal) == 3:
               winning = ClientSocket.recv(1024).decode('utf-8')
               print(winning)
               ClientSocket.send("OK".encode('utf-8'))
               message_what_to_do = ClientSocket.recv(1024).decode('utf-8')
               print(message_what_to_do)
               choice = input()
               if len(choice) > 0:
                   ClientSocket.send(choice.encode('utf-8'))
               else:
                   ClientSocket.send(' '.encode('utf-8'))
                       
               mess = ClientSocket.recv(1024).decode('utf-8')

               if mess == 'Opuszczasz gre':
                   print(mess)
                   break
                   ClientSocket.close()                     
                          
               else:
                   continuing = ClientSocket.recv(1024).decode('utf-8')
                               
                   if continuing == 'Nowa tura':
                       print(continuing)
                       continue
                   if continuing == 'Gra się zamyka':
                       print(continuing)
                       print('Za mało graczy, aby zacząć nową grę ;((')
                             
                       break
                       ClientSocket.close()        

                          
           else:
               print("\nKolejna runda!")
          
       else:
           print(message2)
           my_number = input()
           if len(my_number) > 0:
               ClientSocket.send(my_number.encode('utf-8'))
           else:
               ClientSocket.send(' '.encode('utf-8'))

"""Koniec Fragmentu 2
"""


ClientSocket.close()
