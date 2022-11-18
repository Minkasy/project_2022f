#!/bin/bash
CURRENT=$(cd $(dirname $0);pwd)
EXECUSER=`whoami`
cat << _EOF_ > /etc/systemd/system/projectapi.service
[Unit]
Description = WebAPI for project_2022f
After = network-online.target

[Service]
User = $EXECUSER
WorkingDirectory = $CURRENT
ExecStart = /usr/bin/screen -Dm -S projectapi $CURRENT/start.sh
ExecStop = /usr/bin/screen -S projectapi -X stuff "^C"
Restart = no

[Install]
WantedBy = multi-user.target
_EOF_
systemctl daemon-reload
systemctl enable projectapi.service
systemctl start projectapi.service
