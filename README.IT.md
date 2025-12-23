[![License](https://img.shields.io/github/license/italia/bootstrap-italia.svg)](https://github.com/DavidePapero/AutomateMySlqBackup/LICENSE)
[![ciccio](https://img.shields.io/badge/Status-project_in_beta-blue)](https://github.com/DavidePapero/AutomateMySlqBackup/new/main)

*Read this in other languages: [English](README.md).*

## Automatizza il backup dei tuoi database mysql

Questo progetto l'ho creato per automatizzare il backup a caldo di database mysql senza dovere spendere soldi per comprare utility esterne.

Il backup sono conservati fino al numero indicato dall'utente.

## Prerequisiti

Nella macchina in cui gira è necessario sia installato il docker engine, oppure docker desktop.

## Configurazione

Anche se non si vuole cambiare il comportamento modificando lo script python bisogna comunque configurare il file config.json con i parametri necessari per accedere ai propri database.

Se si vuole che venga mandata una mail reipilogativa andrà configurato l'SMTP.

Se a riga di console si lancia il comando:

```sh
bash setup.txt
```

you compile the docker image and install the relevant container.
Attention you need to configure the volume. In my case the backup files are placed on the host machine in a specific folder. This path must be aligned with the path that appears in the config.json to the "backup_file" and "backup_path" entries


## Prima installazione

Per installare il programma bisogna compilare l'immagine docker e poi lanciare come demone il container
