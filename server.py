# Importations Necessaire 


from fileinput import close
from platform import release
import socket, threading
import math

# On utilise un Mutex pour faire l'execlution mutuelle sans Probleme  

serverMutex=threading.Lock()

#Les actions par le Serveur =>  client :

listActions=[]
listActions.append("consultListVols")
listActions.append("consulterFactureAgence")
listActions.append("consulterTransactionAgence")
listActions.append("recevoir_Facture")
listActions.append("Reservation")
listActions.append("Annulation")
threadLocal=[]
tailleMsg=1024
facture="facture.txt"
vols="vols.txt"
histo="histo.txt"


# Manipulation des threads dans les agences : 


class threadAgences(threading.Thread):

    # Avoir  les coordonnées de l'Agence connectée
    
    def __init__(self,agenceAddress,agenceSocket):
        threading.Thread.__init__(self)
        self.csocket = agenceSocket
        print ("connexion detectée : ", agenceAddress)

    # Avoir  l'action possible pour l'agence connecté 
    
    def run(self):
        print ("connexion d'aprés : ", agenceAddress)
        self.csocket.send(bytes("Response",'utf-8'))
        ch = ''
        while True:
            try:
                data = self.csocket.recv(3072)          
            except socket.error as e:
                print("connexion socket perdu !!")
                break
            ch = data.decode()
            if ch!="Request":
                print("communication par agence attend  une action : ",ch.split(",")[0])
                mdp=ch.split(",")[0]
                if mdp in listActions:
                    NotificationServeur(agenceAddress,ch,self.csocket)
                elif ch=='exit':
                    break
                else:
                    message="action invalide !!"
                    self.csocket.send(bytes(message,'UTF-8'))

        print("Agence address : ", agenceAddress , " est deconnete ..")   
        
# fin de la classe

#Envoie d'un message de Notification au serveur contient l'action effectué par l'agence :

def NotificationServeur(ip,mess,csock):
    elements=mess.split(",")
    if elements[0] == "consultListVols":
        message=consulter_list_vols(elements[1])
        csock.send(bytes(message,'UTF-8'))
    if elements[0] =="consulterFactureAgence":
        message=consulter_facture_agence(elements[1])
        csock.send(bytes(message,'UTF-8'))     
    if elements[0] == "consulterTransactionAgence":
        message=consulter_historique_transaction(elements[1])
        csock.send(bytes(message,'UTF-8'))
    if elements[0] == "recevoir_Facture":
        message=recevoirFacture(elements[1])
        csock.send(bytes(message,'UTF-8'))    
    if elements[0] == "Reservation":
        serverMutex.acquire()
        if  Resrver(int(elements[1]),int(elements[2]),int(elements[3]))==True :  
            message="Reservation avec succes !"
            csock.send(bytes(message,'UTF-8'))
        else:
            message="Reservation invalide , verifiez !"
            csock.send(bytes(message,'UTF-8'))
        serverMutex.release()
    if elements[0] == "Annulation":
        serverMutex.acquire()
        if Annuler(int(elements[1]),int(elements[2]),int(elements[3]))==True:
            message=" Annulation avec succes !"
            csock.send(bytes(message,'UTF-8'))
        else:
            message="Annulation echoue !!"
            csock.send(bytes(message,'UTF-8'))          
        serverMutex.release()
        

#consultation du vol connaisant sa reference : 


def consulter_list_vols(ref):
    vols =open("vols.txt",'r') 
    lnvol = vols.readlines()
    for i in lnvol:
        cl=i.split(',')
        if int(cl[0])==int(ref):
            message ="\nla refernce : {} \n  Destination  :{} \n Nbr Places : {} \n Prix place : {} ".format(int(cl[0]),cl[1],cl[2],cl[3])
            return  message
    return "pas de vol avec cette reference !"        
        

# Consultation de la facture d'une Agence : 

def consulter_facture_agence(ref):
    facture =open("facture.txt",'r') 
    lnfact = facture.readlines()
    for i in lnfact:
        cl=i.split(',')
        if int(cl[0])==int(ref):
            return "la facture a payer est :"+cl[1]
    return "pas de facture avec cette reference !"
        
        
# Consultation de l'historique de transactions

def consulter_historique_transaction(ref):
    res=""
    histo =open("histo.txt",'r') 
    lnhisto = histo.readlines()
    for i in lnhisto:
        cl=i.split(',')
        if int(cl[1])==int(ref):
            res+=" \nReference du vol :{} \n  agence:{}  \n Transaction:{} \n  Valeur:{}\n Resultat:{} \n ------ \n ".format(cl[0],cl[1],cl[2],cl[3],cl[4])
    histo.close()
    if res=="":
        res="Pas de transaction faite pour cette agence !"
    return res        
    








# on verifie existance du reservation 

def verificationVol(ref):
    vols=open("vols.txt","r")
    lnvol = vols.readlines()
    vols.close()
    for i in range(len(lnvol)):
        cl=lnvol[i].split(',')
        if int(cl[0])==ref :
         return True
    return False



#fonction pour calculer la valeur total de chaque vol apres l'ajout et l'annulation 


def calcul (refvol,capacite):
   nb=0
   histo=open("histo.txt","r")
   lnhisto=histo.readlines()
   histo.close()
   for i in range(len(lnhisto)):
            clhisto=lnhisto[i].split(',')
            if (int(clhisto[0])==int(refvol)) & (clhisto[4]=="succes\n")  :
              if clhisto[2]=="Demande":
                 nb+=int(clhisto[3])
              if clhisto[2]=="Annulation" :
                 nb-=int(clhisto[3])  
   nb=capacite-nb
   return nb 
   
   
   
   
# Reservation du vol si c'est possible et faire les mise a jour necessaire dans facture.txt et histo.txt 

def Resrver(ref,nb,refAgence):
    var=0
    bol=False
    if(verificationVol(ref)):
        fact=open(facture,"r") 
        lnfact=fact.readlines()
        fact.close()
        vols=open("vols.txt","r")
        lnvols=vols.readlines()
        vols.close()
        for i in range(len(lnvols)):
            cl=lnvols[i].split(',')
            if int(cl[0])==int(ref):
                  if nb <= calcul(ref,int(cl[2])):
                     o=0
                     for j in range(len(lnfact)):
                        cl2=lnfact[j].split(',')
                        o+=1
                        aux=cl2[0]
                        if int(aux)==int(refAgence):
                                cl2[1]=int(cl2[1])+(nb*int(cl[3]))
                                lnfact[j]="{},{}\n".format(aux,cl2[1])
                                bol=True
                                break
                     if o==len(lnfact)-1 & bol==False :
                        u=nb*int(cl[3])
                        lnfact.append("{},{}".format(refAgence,u))
                     fact=open("facture.txt","w") 
                     for i in lnfact :
                        fact.write(i)
                     fact.close()            
                     histo=open("histo.txt","a")
                     histo.write("{},{},{},{},{}\n".format(ref,refAgence,"Demande",nb,"succes") )
                     histo.close() 
                     return True
                  else :    
                     histo=open("histo.txt","a")
                     histo.write("{},{},{},{},{}\n".format(ref,refAgence,"Demande",nb,"impossible") )
                     histo.close()
                     return False 
    else:
       histo=open("histo.txt","a")
       histo.write("{},{},{},{},{}\n".format(ref,refAgence,"Demande",nb,"impossible") )
       histo.close()
       return False
       
       
# Annulation du vol si c'est possible et faire les mise a jour necessaire dans facture.txt et histo.txt                    
                   
                   
def Annuler(ref,nb,refAgence):
    if(verificationVol(ref)):
        hist=open("histo.txt","r") 
        lnhisto=hist.readlines()
        hist.close()
        vols=open("vols.txt","r")
        lnvols=vols.readlines()
        vols.close()
        compteur=0
        prix=0
        for i in range(len(lnvols)):
            cl=lnvols[i].split(',')
            if int(cl[0])==int(ref):
               prix=int(cl[3])
        for j in range(len(lnhisto)):
             clhisto=lnhisto[j].split(',')
             if (int(ref)==int(clhisto[0]) and int(refAgence)==int(clhisto[1]) and clhisto[4]=='succes\n') :
               if  clhisto[2]=="Demande" :
                  compteur+=int(clhisto[3])
               else  :
                  compteur-=int(clhisto[3])
        print(compteur)
        if compteur>=nb :  
              hist=open("histo.txt","a")    
              hist.write("{},{},{},{},{}\n".format(ref,refAgence,"Annulation",nb,"succes") )
              hist.close()
              fact=open("facture.txt","r")
              lnfact=fact.readlines() 
              fact.close()
              
              for i in range(len(lnfact)):
                fl=lnfact[i].split(',')
                if int(fl[0])==int(refAgence):
                   fl[1]=int(int(fl[1])-(0.9*nb*prix))      
                   lnfact[i]="{},{}\n".format(refAgence,fl[1]) 
              fact=open("facture.txt","w")
              for k in lnfact :
                   fact.write(k)
              fact.close()
              return True
                   
        else:
             
              hist=open("histo.txt","a")    
              hist.write("{},{},{},{},{}\n".format(ref,refAgence,"Annulation",nb,"impossible") )
              hist.close()
              return False
    else:
              hist=open("histo.txt","a")    
              hist.write("{},{},{},{},{}\n".format(ref,refAgence,"Annulation",nb,"impossible") )
              hist.close()
              return False




      
               
#fonction de recevoir de facture pour l'agence de reference refAgence :                 
                  
def recevoirFacture(refAgence):
     message='pas d agence de cette reference !'
     fact=open("facture.txt",'r')
     lnfact=fact.readlines() 
     for i in range(len(lnfact)):
          fl=lnfact[i].split(',')
          if int(fl[0])==int(refAgence):    
            message="la somme a payer est : {} ".format(fl[1])                                
     fact.close()
     return   message


            

LOCALHOST = ""
PORT = 8084
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

print("Serveur en cours d'execution\n")
print("En attente pour les Demandes des Agences..\n")
while True:
    # Boucle principale
    server.listen(1)
    agenceSock, agenceAddress = server.accept()
    # retourner le couple (socket,addresse)
    newthread = threadAgences(agenceAddress, agenceSock)
    newthread.start()
    threadLocal.append(newthread)            
            
            
            
            
            
            
            
            
            
              
        



















































