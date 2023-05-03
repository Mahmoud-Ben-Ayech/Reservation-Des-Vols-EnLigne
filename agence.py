# Importations Necessaires : 
import os
import socket
clear = lambda: os.system('cls')

# Partie Autorisé par le Serveur : 

  # Consultation de liste de Vols :
  
  
def consultListVols(agence):
    clear()
    print("Saisir la reference du vol à consulter : ",end="")
    reference=input()
    agence.sendall(bytes("consultListVols,{}".format(reference),'UTF-8'))  
  
  
#Consultation de Facture d'une agence  : 
  
  
def consulterFactureAgence(agence):
    clear()
    print("donnez la reference d'agence a consulter sa facture :")
    reference=input()
    agence.sendall(bytes("consulterFactureAgence,{}".format(reference),'UTF-8')) 
  
  
#Consultation d'historique des Transactions : 
  
  
def consulterTransactionAgence(agence):
    clear()
    print("Donnez la reference d'agence pour consulter ses transactions  :")
    reference=input()
    agence.sendall(bytes("consulterTransactionAgence,{}".format(reference),'UTF-8'))  
  

#Realisation des Trasnsactions par l'agence : ( En faisant les modifications et les updates convenables ) :


def realiserTransaction():
  clear()
  print("1- faire une demande de reservation ")
  print("2- faire une annulation de reservation")
  print("3- Recevoir une facture Total")
  print("4- Quitter")
  ch=input()
  while(int(ch) not in [1,2,3,4]):
    print("choix incorrecte  ,choisissez entre  1,2,3,4   !!!!!")
    ch=input()
  message=""
  if int(ch)==1:
    print("donnez la reference de votre agence ")
    agencee=input()
    print("donnez la reference de vol ")
    reference=input()
    print("donnez le nombre de places a reserver")
    nb=input()
    message="Reservation,{},{},{} ".format(reference,nb,agencee)
    agence.sendall(bytes(message,'UTF-8'))  
  if int(ch)==2:
    print("donnez la reference de votre agence ")
    agencee=input()
    print("donnez la reference de vol")
    reference=input()
    print("donnez le nombre de places a annuler")
    nb=input()
    message="Annulation,{},{},{} ".format(reference,nb,agencee)
    agence.sendall(bytes(message,'UTF-8'))  
  if int(ch)==3 :
    recevoir_Facture(agence)
  if int(ch)==4:
    interfaceAgence(agence)


#Recevoir une facture totale pour une agence donnée


def recevoir_Facture(agence) :
    clear()
    print("Saisir la reference du votr agence  : ",end="")
    agencee=input()
    agence.sendall(bytes("recevoir_Facture,{}".format(agencee),'UTF-8'))  


#Interface  Agence de voyage : 


def interfaceAgence(agence):
  clear()
  choix=0
  print("1- consulter la liste des Vols")
  print("2- consulter la facture de votre agence")
  print("3- consulter l'historique du transaction de l'agence ")
  print("4- faire  une transaction")
  print("choix d'action :",end="")
  choix=input()
  while int(choix) not in [1,2,3,4]:
    print(" choix incorrecte  ,choisissez entre  1,2,3,4 !!!!!")
    choix=input()
  if(int(choix) ==1):
    consultListVols(agence)
  if(int(choix) ==2):
    consulterFactureAgence(agence)  
  if(int(choix) ==3):
    consulterTransactionAgence(agence)
  if(int(choix) ==4):
    realiserTransaction()
  


#le socket SOCK_STREAM utilise  le protocole TCP  et le socket  SOCK_DGRAM utilise le protocole UDP


SERVER = "127.0.0.1"
PORT = 8084
agence = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
agence.connect((SERVER, PORT))
agence.sendall(bytes("Request",'UTF-8'))
ln =  agence.recv(30720)
while True:

 interfaceAgence(agence) 
 ln =  agence.recv(5072)
 if(ln.decode()!="Request"):
    clear()
    print("From Server :" ,ln.decode())
    input("Press Enter to continue...")  
    if(ln.decode()=="exit"):
       break
agence.close()













  
