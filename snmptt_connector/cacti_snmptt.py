#!/usr/bin/python3

### connect to MariaDB database

### import modules
import mariadb
import logging
import os
import sys
from datetime import datetime
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name('.env'))

logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO').upper(),
    filename=os.environ.get('LOG_FILE') or None,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)


# Define Arguments for variables from snmptt
parser = argparse.ArgumentParser(description = 'SNMPTT Variables')

parser.add_argument('--hostname', help = "Device Hostname", required=True)
parser.add_argument('--alert', help = "Alert Messege", required=True)
parser.add_argument('--facility', help = "Alert Facility", required=True)
parser.add_argument('--priority', help = "Alert Priority", required=True)



args = parser.parse_args(sys.argv[1:])

if args.hostname is not None: ({'device Hostname': args.hostname}) 
if args.alert is not None: ({'Alert Messege': args.alert})
if args.facility is not None: ({'Alert facility': args.facility})
if args.priority is not None: ({'Alert priority': args.priority})



### connect to database
db = None
cursor = None
try:
    db = mariadb.connect(
        host = os.environ.get('DB_HOST', 'localhost'),
        user = os.environ['DB_USER'],
        password = os.environ['DB_PASSWORD'],
        database = os.environ['DB_NAME'],
        autocommit = False
    )

    ### create cursor
    cursor = db.cursor()

    ### write to database
    sql = "INSERT INTO syslog_incoming (facility_id, priority_id, program, logtime, host, message) VALUES (?, ?, ?, ?, ?, ?)"
    val = (args.facility,args.priority, "traps", datetime.now(),args.hostname, args.alert)
    cursor.execute(sql, val)
    db.commit()
except (mariadb.Error, KeyError):
    if db is not None:
        db.rollback()
    logger.error("Unable to write to database")
    sys.exit(1)
finally:
    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()

