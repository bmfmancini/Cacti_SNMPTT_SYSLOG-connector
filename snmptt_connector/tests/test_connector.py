import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / 'cacti_snmptt.py'


class ConnectorTests(unittest.TestCase):
    def run_connector(self, failure=None, log_settings=None):
        driver = Mock(Error=RuntimeError)
        dotenv = Mock()
        db = driver.connect.return_value
        cursor = db.cursor.return_value
        if failure:
            getattr(cursor if failure == 'execute' else db, failure).side_effect = RuntimeError('failed')
        with patch.dict(sys.modules, {'mariadb': driver, 'dotenv': dotenv}), \
                patch.dict(os.environ, {'DB_USER': 'test', 'DB_PASSWORD': 'secret', 'DB_NAME': 'syslog', **(log_settings or {})}, clear=True), \
                patch.object(sys, 'argv', [str(SCRIPT), '--hostname', 'router', '--alert', "trap's message", '--facility', '2', '--priority', '6']), \
                patch('logging.basicConfig') as configure, \
                patch('logging.getLogger') as get_logger:
            if failure:
                with self.assertRaises(SystemExit) as raised:
                    runpy.run_path(str(SCRIPT), run_name='__main__')
                self.assertEqual(raised.exception.code, 1)
            else:
                runpy.run_path(str(SCRIPT), run_name='__main__')
        configure.assert_called_once_with(
            level=(log_settings or {}).get('LOG_LEVEL', 'INFO').upper(),
            filename=(log_settings or {}).get('LOG_FILE') or None,
            format='%(asctime)s %(levelname)s %(message)s',
        )
        if failure:
            get_logger.return_value.error.assert_called_once_with('Unable to write to database')
            get_logger.return_value.info.assert_not_called()
        else:
            get_logger.return_value.info.assert_called_once_with('Successfully wrote to database')
        dotenv.load_dotenv.assert_called_once_with(SCRIPT.with_name('.env'))
        driver.connect.assert_called_once_with(host='localhost', user='test', password='secret', database='syslog', autocommit=False)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        return db, cursor

    def test_success_commits_bound_insert(self):
        db, cursor = self.run_connector()
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        sql, values = cursor.execute.call_args.args
        self.assertEqual(sql.count('?'), 6)
        self.assertEqual(values[:3], ('2', '6', 'traps'))
        self.assertEqual(values[4:], ('router', "trap's message"))

    def test_insert_failure_rolls_back(self):
        db, _ = self.run_connector('execute')
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_commit_failure_rolls_back(self):
        db, _ = self.run_connector('commit')
        db.rollback.assert_called_once()

    def test_logging_settings(self):
        self.run_connector(log_settings={'LOG_LEVEL': 'warning', 'LOG_FILE': '/tmp/connector.log'})


if __name__ == '__main__':
    unittest.main()
