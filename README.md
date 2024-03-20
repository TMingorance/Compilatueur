# Compilatueur
Student Python project about compiling a homemade programming language

Compilatueur est un projet d'école d'ingénieur réalisé en 2020, en équipe de 3, et qui a consisté en la création d'un compilateur de code "maison" : Avec les commandes d'exécution ci-dessous, ce projet permet de parser du code écrit dans un langage "maison" pour le traduire en langage machine.\
\
\
\
Pour lancer le compilateur, il faut déjà avoir téléchargé python3, ouvrez une console de commande depuis le dossier "Compilatueur", puis écrivez la commande suivante :

Sous Windows :

<Chemin d'accès vers l'executable de Python3> src\Main.py <l'adresse du fichier texte contenant le code à compiler>

Sous Linux :

    méthode 1:
            #Déplacez-vous vers le répertoire contenant nos fichiers sources
            cd ./chemin/src
            python3 Main.py [OPTIONS] ../chemin/fichier_test.nno [OPTIONS]
    méthode 2:
            #Exécutez depuis n'importe quel répertoire en utilisant les chemins absolus ou relatifs
            python3 /chemin/absolu/src/Main.py [OPTIONS] /chemin/absolu/fichier_test.nno [OPTIONS]
            

OPTIONS:            
    Il est possible d'ajouter l'option suivante après le fichier source :

    -d pour afficher les instructions de debug
    
NOTE: 
    Dans la version actuelle, l'exécution de Main.py et anasyn.py sont les mêmes.
    Il est cependant recommandé d'utiliser Main.py car anasyn.py est susceptible d'être modifié pour des besoins de tests et déboggage
