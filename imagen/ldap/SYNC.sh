#!/bin/sh

LDAP_HOST=imagen2.cea.fr
LDAP_PORT=389
LDAP_LOCAL_PORT=3389

ROOT=`dirname $0`

ssh imagen2 -f -L ${LDAP_LOCAL_PORT}:${LDAP_HOST}:${LDAP_PORT} sleep 60
"${ROOT}/extract_xnat_accounts.sh" | "${ROOT}/import_xnat_accounts.py" -l "ldap://localhost:${LDAP_LOCAL_PORT}"
