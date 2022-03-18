# -*- coding: utf-8 -*-
"""
@author: Aleksandra Sidor, Justyna Budzyńska
"""

"""Gra wieloosobowa - podaj liczbe najblizsza sredniej

Gra polega na wymysleniu przez graczy liczby z przedzialu
(0,20>, ktora bedzie najblizsza sredniej wyznaczonej z podanych przez graczy 
liczb. Punkt otrzymuje gracz, ktorego strzal byl najblizszy sredniej. Jednak
gdy wiecej niz jeden gracz byl najblizej sredniej, otrzymuja oni punkty ujemne, 
przy czym minimalna liczba punktow wynosi 0.

Aby gra sie zaczela, wymagane jest co najmniej 4 graczy. Gra konczy sie 
w momencie osagniecia przez ktoregosc z graczy 3pkt.Gra moze byc rozegrana jest
raz w momencie, gdy co najmniej 4 graczy z poprzedniej rundy bedzie chcialo ja
kontynuowac.

Aby poprawnie zaczac gre, nalezy uruchomic plik serwera server.py oraz co
najmniej 4 pliki klienta/gracza client.py (w przypadku gdy uruchomiona zostanie
mniej plikow lub zadnen plik client.py, gra sie nie rozpocznie i zostanie
wyslana wiadomosc o zbyt malej ilosci graczy). 
Pliki mozna uruchomic albo w terminalu komputera, albo w srodowisku 
programistycznym odpowiednim dla pythona.

To jest plik obslugiwany przez serwer.

"""

import socket



ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
port = 5050

playersCount = 0    #liczba polaczen = liczba graczy
numbers = []        #liczby (strzały) od graczy
scores = []         #punkty graczy
diffs = []          #odległosc liczb (strzałów) od sredniej 
nicks = []          #nicki graczy
clients = []        #adresy i porty graczy
addresses = []      #porty graczy

max_score = 2       #maksymalna mozliwa liczba punktow do zdobycia
maximal = 0         #aktualna maksymalna liczba punktow (w tablicy scores)



try:
    ServerSocket.bind((host,port))
except socket.error as e:
    print(str(e))

print('Oczekiwanie na graczy...')
ServerSocket.listen()
ServerSocket.settimeout(45)

def sending(msg):
    """Funkcja wysylajaca wiadomosc do wszystkich podlaczonych klientow

    Parameters
    ----------
    msg : str
        Wiadomosc, ktora ma zostac wyslana

    Returns
    -------
    None.

    """
   
    for client in clients:
        client.sendall(msg.encode('utf-8'))


def broadcast(msg): 
    """Funkcja pobierajaca i sprawdzajaca liczby wysylane przez klientow
       do zmiennej numb pobierany jest strzał od klienta, po czym sprawdzane 
       jest czy strzal jest integerem oraz czy miesci sie w okreslonym zakresie,
       jesli tak, wartosc wprowadzana jest do tablicy numbers
    

    Parameters
    ----------
    msg : str
        Wiadomosc, wysylajaca zadanie przeslania liczby przez klienta

    Returns
    -------
    None.

    """
    
    global numbers
    for client in clients:
         tmp = True
         while tmp:
             client.sendall(msg.encode('utf-8'))
             numb = client.recv(1024).decode('utf-8')
             if numb.isdigit() is True:
                 numb = int(numb)
                 if (numb > 0 and numb < 21):
                     numbers.append(numb)
                     tmp = False
                     

def game():
    """Funkcja obslugujaca gre
        obliczana jest srednia z wszytskich liczb pobranych od klientow,
        wyznaczane sa moduly roznicy liczb i sredniej wartosci, nastepnie 
        wybierana jest najmniejsza odleglosc (z tablicy diffs) i graczom 
        przyznawane sa punkty (tablica scores)
        do klientow wysylana jest punktacja po kazdej rundzie

    Returns
    -------
    None.

    """

    global scores
    global diffs
    sum = 0
    for i in numbers:
        sum = sum + i #sumowanie zebranych strzałów od graczy
    mean = sum/len(numbers) #srednia
    print(f"\nŚrednia po tej rundzie: {mean}") 
            
    for j in numbers:
        diffs.append(abs(j - mean)) #odległosć strzału od sredniej liczona dla każdego uczestnika
    print(f"Odległosć poszczególnych strzałóW od sredniej: {diffs}") 
    minimal = numbers[diffs.index(min(diffs))] 
    print(f"Wartosc strzału, który był najbliżej sredniej: {minimal}") 
            
    minimal_diffs = min(diffs)
    ind = [i for i in range(len(diffs)) if diffs[i] == minimal_diffs]
    #przyznawanie punktów
    if len(ind) == 1:
        scores[ind[0]] += 1
    else:
        for x in ind:
            if scores[x] <= 0:
                scores[0] = 0
            else:
                scores[x] -= 1
    
    D1 = dict(zip(nicks, numbers)) #słownik ze strzałami klucz:wartosc -> nick:strzał w danej rundzie
    D2 = dict(zip(nicks,scores)) #słownik z punktacją klucz:wartosc -> nick:punkty
    
    print(f"STRZAŁY W TEJ RUNDZIE:\n{D1}") 
    print(f"PUNKTACJA PO TEJ RUNDZIE:\n{D2}")    

    
    msg = f"\nPunktacja po tej rundzie wygląda następująco: \n{D2}"

    sending(msg)
    sending(str(max(scores)))



def starting():
    """Funkcja uruchamiajaca gre i ustawiajaca poczatkowe wartosci 
        punktow
        funkcja wywoluje funkcje broadcast() i game() dopoki jeden z graczy nie
        osiagnie 3pkt, jesli tak wyznaczany jest zwyciezca i wysylana jest
        informacja do klientow
    

    Returns
    -------
    None.

    """
    
    global scores
    global maximal
        
    scores = list(range(playersCount))
    scores = [0]* len(scores)
    maximal  = max(scores)

    while maximal <= max_score:
        msg = "Podaj liczbe w zakresie (0,20>.\nTwój strzał:"
        broadcast(msg)
        sending('ok')               
        game()
        maximal = max(scores)
        diffs.clear()
        numbers.clear()
                
    indx = scores.index(maximal)
    win = f"\n!!!KONIEC GRY!!!\nWygrywa: {nicks[indx]}"
    winner = "\n!!!KONIEC GRY!!!\nWygrałeś! Gratulacje!"

    for client in clients:
        if client == clients[indx]:
            client.send(winner.encode('utf-8'))
        else:
            client.sendall(win.encode('utf-8'))
    #print("csok")
    for client in clients:
        ok = client.recv(1024).decode('utf-8')
        

def main():
    """Funkcja glowna programu
        przyjmowani sa klienci i wysylane jest żądanie z podaniem nicku oraz
        sprawdzana jest jego poprawnosc, po uplywie okreslonego czasu (?), jesli 
        liczba klientow jest wystarczajaca, wywolywana jest funkcja starting();
        po ogloszeniu wynikow gry, zerowane sa liczniki i wysylane jest 
        zapytanie o jej ponowne przeprowadzenie; jesli liczba graczy jest 
        nie mniejsza niz 4, gra jest ponownie uruchamiana
    

    Returns
    -------
    None.
    
    """
    
    global clients
    global addresses
    global nicks
    global scores
    global diffs
    global numbers
    global playersCount
    global max_score
    
    while True:
        try:     
            client, address = ServerSocket.accept()
            print(address)
            addresses.append(address[1])
            print(addresses)
            print('Połączono z : ' + address[0] + ': ' + str(address[1]))
            playersCount +=1
            tmp = True
            client.send("Podaj swój nick:".encode('utf-8'))
    
            while tmp:
                username = client.recv(1024).decode('utf-8')
    
                if (username.isdigit() is True or username == ' '):
                    client.send("Nieprawidłowy nick. Podaj swój nick jeszcze raz:".encode('utf-8'))
                    
                elif nicks.count(username)==1:
                    client.send("Ten nick jest już zajęty. Podaj inny nick: ".encode('utf-8'))
                else:
                    client.send("Udało się! Wchodzisz do gry!".encode('utf-8'))
                    nicks.append(username)
                    clients.append(client)
                    tmp = False
            print(f"Liczba graczy: {playersCount}: {nicks}")
        except socket.timeout:
            if playersCount < 4:
                print("Za mało graczy")
                #zerowanie liczników, bo zgłosiło się zbyt mało graczy
                if playersCount != 0:
                    msg = "koniec"
                    sending(msg)
                    client.close()
                    nicks.clear()
                    addresses.clear()
                    clients.clear()
                    playersCount = 0
                break
                ServerSocket.close()
            else:
                msg = f"Jest {playersCount} graczy. Gra się rozpoczyna\n"
                sending(msg)
                
                cont = True
                while cont:  
                    starting()
                    ending = []
                    for client in clients:
                        again = "\nChcesz zagrać jeszcze raz? \nJesli tak kliknij 't' na klawiaturze!\nJesli nie kliknij dowolny przycisk na klawiaturze"            
                        end = "Opuszczasz gre"
                       # print("ocb tu")
                        #print("dezycje")
                        client.send(again.encode('utf-8')) 
                        #print("czytanie")
                        choice = client.recv(1024).decode('utf-8')
                        if choice.isdigit() is False:
                            choice = str(choice) 
                            numbers.clear()
                            diffs.clear()
                            scores.clear()
                            maximal = 0
                            
                            if choice == 't':
                                client.send('chcesz grac dalej!'.encode('utf-8'))
                            else:
                                client.send(end.encode('utf-8'))
                                ind = addresses.index(client.getpeername()[1])
                                ending.append(ind)
                                playersCount -= 1
                                print(f"Klient o porcie: {client.getpeername()[1]} wyszedł z gry")
                                print(f"W grze pozostało {playersCount} graczy")
                        else:
                            client.send(end.encode('utf-8'))
                            
                    lista_ad = []
                    lista_nic = []
                    lista_cl = []
                    
                    for i in ending:
                        lista_ad.append(addresses[i])
                        lista_nic.append(nicks[i])
                        lista_cl.append(clients[i])
                        
                    for el in lista_ad:
                        addresses.remove(el)
                    for el in lista_nic:
                        nicks.remove(el)
                    for el in lista_cl:
                        clients.remove(el)
                    

                            
                    '''jesli nie zostanie wystarczająca liczba graczy (4) okienka graczy i servera się zamykają, wszystkie
                    liczniki zostają wyzerowane'''
                            
                    if playersCount < 4:
                        msg = 'Gra się zamyka'
                        sending(msg)
                        #zerowanie liczników, bo zgłosiło się za mało graczy
                        sending(msg)
                        nicks.clear()
                        addresses.clear()
                        clients.clear()
                        playersCount = 0
                        print("KONIEC.")
                        ServerSocket.settimeout(1)
                        break
                        ServerSocket.close()
                        
                    #jesli jest wystarczająca liczba graczy gra rozpoczyna się ponownie (bez podawania nicków)
                    else:
                        msg = 'nowa tura'
                        sending(msg)
                        print("gramy dalej")
                        continue
 

main()

ServerSocket.close()