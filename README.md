[![License](https://img.shields.io/github/license/italia/bootstrap-italia.svg)](https://github.com/DavidePapero/AutomateMySlqBackup/LICENSE)
[![ciccio](https://img.shields.io/badge/Status-project_in_beta-blue)](https://github.com/DavidePapero/AutomateMySlqBackup/new/main)

*Leggi questo in un'altra lingua: [Italian](README.IT.md).*

## Automate the backup of your mysql databases

I created this project to automate hot backup of mysql databases without having to spend money money to buy external utilities.

Backups are kept up to the number indicated by the user.

## Prerequisites

The docker engine or docker desktop must be installed on the machine on which it runs.

## Configuration

Even if you don't want to change the behavior you still need to modify the python script configure the config.json file with the parameters necessary to access your databases.

If you want a summary email to be sent, SMTP will need to be configured.

If you run the command from the console:

```sh
bash setup.txt
```

you compile the docker image and install the relevant container.
Attention you need to configure the volume. In my case the backup files are placed on the host machine in a specific folder. This path must be aligned with the path that appears in the config.json to the "backup_file" and "backup_path" entries

## First installation

To install the program you need to compile the docker image and then launch the container as a daemon.