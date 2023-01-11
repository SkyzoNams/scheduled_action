from scheduled_action.src.node_collapser import Node_Collapser
from scheduled_action.src.DataBaseUtils import DataBaseUtils
import argparse
import logging
import datetime
import os
import traceback

parser = argparse.ArgumentParser(description='Execute scheduled actions')
parser.add_argument('-pub', dest='pubkey', help='the deployed node pubkey.', required=True)
parser.add_argument('-date', dest='initial_scheduling', help="the cron initial scheduling date", required=True)
parser.add_argument('-filename', dest='validator_filename', help="the validator keys filename", required=True)
parser.add_argument('-period', dest='locked_period', help="the instance locked period", required=True)

logging.basicConfig(format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO)
logging.addLevelName(21, "SUCCESS")

def main():
    try:
        collapser = Node_Collapser(parser.parse_args())
        if collapser.is_cron_record() is True and collapser.is_period_over(parser.parse_args().initial_scheduling) is True:
            collapser.execute_node_collapse_endpoint()
            collapser.update_data_record_status()
            collapser.disable_cron()
            collapser.update_is_executed()
            logging.log(21, "all the scheduled actions are now executed!")
    except Exception as e:
        insert_error(str(traceback.format_exc()), parser.parse_args().pubkey, e)
        raise e

def insert_error(error, pubkey, raised_error):
    if pubkey is not None:
        staking_id = DataBaseUtils().get_investment_staking_id_by(pubkey)
        contract_address = DataBaseUtils().get_investment_address_by(staking_id)
    DataBaseUtils().insert_error(error, str(contract_address), "scheduled_action_executer", raised_error)
    
def write_error_on_file(error):
    try:
        if os.path.exists("/mnt/backend"):
            if os.path.exists("/mnt/backend/errors") is False:
                os.mkdir("/mnt/backend/errors")
            if os.path.exists("/mnt/backend/errors/scheduled_action") is False:
                os.mkdir("/mnt/backend/errors/scheduled_action")
            with open("/mnt/backend/errors/scheduled_action/scheduled_action-" + str(datetime.datetime.now()) + ".txt" , 'w') as file:
                file.write(error)
        else:
            logging.warning("\x1b[33;20m'/mnt/backend' not mounted here\x1b[0m")
    except Exception as e:
        raise e
    

if __name__ == "__main__":
    main()