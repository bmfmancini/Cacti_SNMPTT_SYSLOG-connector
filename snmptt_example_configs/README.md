# SNMP trap configuration examples

Flow: device → snmptrapd → snmptthandler → SNMPTT daemon → Python connector → Cacti `syslog_incoming`.

These Linux examples assume the repository is deployed at
`/opt/Cacti_SNMPTT_SYSLOG-connector`. Adjust paths for your installation.
Back up existing configuration before merging these samples.

1. Install Net-SNMP's snmptrapd, SNMPTT, and the connector's Python dependencies.
   If using a virtual environment, use its Python interpreter in every `EXEC`.
   Configure `snmptt_connector/.env` as described in the root README.
2. Merge `snmptrapd.conf` into the receiver's configuration. Replace `CHANGE_ME`
   and the documentation subnet with your community and allowed sender subnet.
   This SNMPv2c example keeps authorization enabled. See the
   [Net-SNMP manual](https://www.net-snmp.org/docs/man/snmptrapd.conf.html)
   for SNMPv3 authorization. Numeric OID output is selected with `outputOption n`.
3. Merge `snmptt.ini.example` into your packaged `snmptt.ini`, usually under
   `/etc/snmp/` or `/etc/snmptt/`. Retain existing event files and service-specific
   daemon settings. Both the handler and daemon must use this configuration.
4. Install `snmptt.connector.conf` at `/etc/snmp/snmptt.connector.conf`.
   Avoid duplicate OID definitions across loaded event files.
5. Ensure the snmptrapd user can write the spool directory and the SNMPTT user
   can process it, read the connector and `.env`, and write `LOG_FILE` if set.
   Keep credentials restricted to the service account. Restart or reload both
   services using your distribution's service manager.

The event examples use `$aA` for the agent IP and `$Fz` for the formatted message.
Link events expect the standard ifIndex, ifAdminStatus, and ifOperStatus varbinds
in that order. The numeric `--priority` is specified per event; changing SNMPTT's
severity label alone does not change the database priority.
See the [SNMPTT EVENT and EXEC documentation](https://snmptt.org/docs/snmptt.shtml#SNMPTT.CONF-EVENT).

For a local smoke test, temporarily authorize `127.0.0.1` with the same community,
then send a numeric coldStart trap (replace the example community):

```sh
snmptrap -v 2c -c CHANGE_ME udp:127.0.0.1:162 '' .1.3.6.1.6.3.1.1.5.1
```

This invokes a real database insert when delivery succeeds. Check receiver and
SNMPTT logs, connector output, and Cacti's syslog view. The connector writes
`program=traps`; Cacti may consume the incoming row before you inspect it.
Unmatched traps have no connector `EXEC` in these examples. An `EXEC` failure
does not provide a durable database retry queue.

These are configuration examples; they have not been tested against running
snmptrapd/SNMPTT services in this repository.
