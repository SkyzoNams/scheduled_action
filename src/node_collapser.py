from crontab import CronTab
from datetime import datetime, timedelta
from scheduled_action.src.DataBaseUtils import DataBaseUtils
from scheduled_action.src.api_caller import API_Caller
import logging
logging.basicConfig(format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO)

class Node_Collapser():
    def __init__(self, parsed_args):
        self.pubkey = parsed_args.pubkey
        self.validator_filename = parsed_args.validator_filename
        self.locked_period = parsed_args.locked_period


    def is_cron_record(self):
        return DataBaseUtils().is_cron_record(self.pubkey, self.validator_filename, self.locked_period)
        
    """
        @Notice: This function will make sure the correct number of days have been elapsed since the cron has been created
        @Dev:    We compare the initial_scheduling date to the current data minus the locked period
    """   
    def is_period_over(self, initial_scheduling_date):
        if datetime.strptime(initial_scheduling_date, '%Y-%m-%d %H:%M:%S.%f') <= datetime.now() - timedelta(days=int(self.locked_period)):
            logging.info("locked period over")
            return True
        else:
            logging.info("locked period not over")
            return False

    """
        @Notice: This function will disable the cron that ran the script
        @Dev:    We get the cron using an id (the pubkey) and remove it
    """
    def disable_cron(self):
        cron = CronTab(user="root")
        cron.remove_all(command=self.pubkey)
        cron.write()

    """
        @Notice: This function will execute the api endpoint to collapse the node
        @Dev:    
    """
    def execute_node_collapse_endpoint(self):
        API_Caller().send_req(api_endpoint="collapse_node", args_list=[self.validator_filename])

    """
        @Notice: This function will update the event_type column from the table using the pubkey
        @Dev:    We use the DataBase_Manager update_event_type function to update the event_type value
    """ 
    def update_data_record_status(self):
        DataBaseUtils().update_event_type(self.pubkey, "collapsing node")
        
    def update_is_executed(self):
        DataBaseUtils().update_is_excecuted_record("cron_store", DataBaseUtils().encryptor.hash_list([self.pubkey, self.validator_filename, self.locked_period]), True)