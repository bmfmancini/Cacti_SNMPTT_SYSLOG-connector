# Cacti_SNMPTT_SYSLOG-connector
This is a simple script to write output from SNMPTT to the Cacti syslog_incoming table 


SNMPTT is a great tool to convert traps sent to SNMPTRAPD to readable messeges
as SNMPTT runs on the local system all syslog  messeges will be displayed as if they come from the local system
in the cacti syslog plugin 

this script allows you to use variable substitution and the EXEC function in snmptt to 
write the host ip and messege direct to the syslog_incoming table

The Trap flow will follow this 

Trap >> SNMPTRAPD >> SNMPTT >> snmptt_syslog.py >> syslog_incoming table

i.e

EVENT Uptime .1.3.6.1.4.1.7342.0.153  "Status Events" Normal
FORMAT Device reinitialized (coldStart)
EXEC /opt/snmptt_syslog.py --hostname $aA --alert "$Fz"  --priority 6  --facility 2
SDESC

