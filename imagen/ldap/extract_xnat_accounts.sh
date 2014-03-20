#!/bin/sh

SQL_DATABASE="imagen"
SQL_REQUEST="SELECT login, firstname, lastname, email, primary_password, primary_password_encrypt, enabled FROM xdat_user;"
PSQL_COMMAND="psql -d '${SQL_DATABASE}' -t -c '${SQL_REQUEST}'"

HOST1="imagen@imagen.partenaires.cea.fr"
HOST2="imagen@imagen-bis.partenaires.cea.fr"

ssh $HOST1 "ssh $HOST2 \"$PSQL_COMMAND\""
