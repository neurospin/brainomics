CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME

cubicweb-ctl stop $INSTANCENAME
cubicweb-ctl delete $INSTANCENAME
cubicweb-ctl create $CUBENAME $INSTANCENAME
cubicweb-ctl start $INSTANCENAME
