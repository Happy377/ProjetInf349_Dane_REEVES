# ProjetInf349_Dane_REEVES
Flask API with Peewee ORM and PostGreSQL Database. Has the files to be containerized.

Toute la partie REDIS Queue ne fonctionne pas et je crois pas être le seul: https://github.com/rq/rq/pull/1852
J'ai tout de même laissé le code en commentaire.

Tout le côté docker fonctionne avec les variables d'environnement données. Je me suis permis de faire un bridge entre les services et de mettre l'API dans 
le docker-compose.yml pour que ce soit fonctionnel.

La partie Front-end n'est pas aboutie, j'ai préféré pas trop passer de temps dessus.

La partie création de l'API à été complété; elle n'était pas très avancé pour le premier rendus.
