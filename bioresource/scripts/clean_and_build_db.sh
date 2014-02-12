CUBENAME=bioresource
INSTANCENAME=inst2_$CUBENAME

cubicweb-ctl stop $INSTANCENAME
cubicweb-ctl delete $INSTANCENAME
cubicweb-ctl create $CUBENAME $INSTANCENAME
cubicweb-ctl start $INSTANCENAME
