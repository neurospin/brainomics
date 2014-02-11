The expected input of script "import_xnat_accounts.py" is the output
of the following command:
 psql -t -c 'SELECT login, firstname, lastname, email, primary_password, primary_password_encrypt, enabled FROM xdat_user;'

See also:
https://bioproj.extra.cea.fr/redmine/projects/imagen/wiki/234_Imagen_v2_SFTP#Exportation-et-injection-des-comptes-XNAT-dans-LDAP
