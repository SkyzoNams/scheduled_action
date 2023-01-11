#/usr/bin/python3
import argparse
import os
from datetime import datetime, timedelta
from crontab import CronTab
from scheduled_action.src.DataBaseUtils import DataBaseUtils
import logging
logging.basicConfig(format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO)
logging.addLevelName(21, "CRON ACTION")
import traceback

parser = argparse.ArgumentParser(description='Execute scheduled actions')
parser.add_argument('-addr', dest='contract_address', help='the contract address to listen.', required=True)
parser.add_argument('-pubkey', dest='pubkey', help='deposit data pubkey', required=True)
parser.add_argument('-call', dest='caller', help='the contract deployer public address.', required=True)
parser.add_argument('-period', dest='locked_period', help="staking instance locked period", required=True)
parser.add_argument('-filename', dest='validator_filename', help="the validator keys filename", required=True)


class Cron_Creator:
    def __init__(self, parsed_args):
        if isinstance(parsed_args, dict):
            self.pubkey = parsed_args['pubkey']
            self.caller = parsed_args['caller']
            self.locked_period = parsed_args['locked_period']
            self.validator_filename = parsed_args['validator_filename']
        else:
            self.pubkey = parsed_args.pubkey
            self.caller = parsed_args.caller
            self.locked_period = parsed_args.locked_period
            self.validator_filename = parsed_args.validator_filename

    """
        @Notice:  This function will return the current date + the number of locking period days
        @Dev:     The date is returned as datetime.date type, using timedelta to add a number of days to the current date
    """
    def get_scheduled_date(self):
        return datetime.now() + timedelta(days=int(self.locked_period))

    """
        @Notice:  This function will create a cron. This cron will execute on sudo mode the scheduled_action.py script using the absolute path with 
                the right parameters.
        @Dev:     The use the Crontab lib and schedule it using the scheduled_date given in parameters.
    """
    def create_cron(self):
        if len(DataBaseUtils().select_by_row_hash("cron_store", [self.pubkey, self.validator_filename, self.locked_period])) == 0:
            scheduled_date = self.get_scheduled_date()
            date = str(datetime.now())
            with CronTab(user="root") as cron:
                command = "sudo /usr/local/bin/python3 " + os.path.abspath("") + "/scheduled_action_executor.py -pub " + self.pubkey + " -date '" +  date + "' -filename " + self.validator_filename + " -period " + self.locked_period + " > /tmp/error.log 2>&1"
                job = cron.new(command=command, comment=self.pubkey)
                job.minute.on(int(scheduled_date.strftime("%M")))
                job.hour.on(int(scheduled_date.strftime("%H")))
                job.month.on(int(scheduled_date.strftime("%m")))
                job.day.on(int(scheduled_date.strftime("%d")))
            DataBaseUtils().insert_cron_record(command, self.pubkey, self.validator_filename, self.locked_period, scheduled_date)
            logging.log(21, command)
            logging.info('-> Cron created for ' + str(scheduled_date)) 
        else:
            logging.warning('cron already created')


def run(pubkey, caller, locked_period, validator_filename):
    try:
       Cron_Creator({"pubkey": pubkey, "caller": caller, "locked_period": locked_period, "validator_filename": validator_filename}).create_cron()
    except Exception as e:
        insert_error(str(traceback.format_exc()), pubkey, e)
        raise e

def insert_error(error, pubkey, raised_error):
    if pubkey is not None:
        staking_id = DataBaseUtils().get_investment_staking_id_by(pubkey)
        contract_address = DataBaseUtils().get_investment_address_by(staking_id)
    DataBaseUtils().insert_error(error, str(contract_address), "cron_creator", raised_error)

def main():
    try:
       Cron_Creator(parser.parse_args()).create_cron()
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()