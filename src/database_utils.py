from datetime import datetime
from scheduled_action.src.Secrets import Encrypt
from scheduled_action.src.DatabaseDriver import DatabaseDriver
import logging
import os

class DataBaseUtils(object):
    def __init__(self):
        self.encryptor = Encrypt()
        self.db = DatabaseDriver()

    """
     @Notice: This function with select all the item stored in the database
     @Dev:    We first connect to the database, then we execute the SELECT query.
              Finally we use the fetchall method to get the items, we disconnect to the database and return the items
    """
    def select_all(self, table_name):
        query = "SELECT * FROM " + table_name
        items = self.db.execute(execution_string=query, fetch_all=True)
        return items

    """
     @Notice: This function will select from the database all the items with not_checked value equal to False
     @Dev:   We first build our select query then we execute it and return the fetchall list returns
    """
    def select_not_checked_records(self, table_name):
        query = "SELECT * FROM " + table_name + " WHERE is_checked = False ORDER BY id"
        items = self.db.execute(execution_string=query, fetch_all=True)
        return items

    """
     @Notice: This function will update the is_checked value regarding the item id
     @Dev:    We first build our update query then we execute it
    """
    def update_is_checked(self, item_id, is_checked):
        query = "UPDATE " + self.table + \
            " SET is_checked = {is_checked}  WHERE id = {id}".format(
                is_checked=is_checked, id=item_id)
        self.db.execute(execution_string=query, commit=True)

    """
     @Notice: This function will decrypt the encrypted record and return a formatted dict
     @Dev:    We create and return a formatted dict with the decrypted values, using the decrypt_message() from the encryptor instance
    """
    def decrypte_record(self, record):
        return {
            "id": record[0],
            "public_key": record[1],
            "staking_id": int(self.encryptor.decrypt_message(record[2].tobytes())),
            "withdrawal_credentials": self.encryptor.decrypt_message(record[3].tobytes()),
            "signature": self.encryptor.decrypt_message(record[4].tobytes()),
            "deposit_data_root": self.encryptor.decrypt_message(record[5].tobytes()),
            "is_checked": record[6],
            "locked_period": int(self.encryptor.decrypt_message(record[7].tobytes())),
            "created": datetime.strptime(self.encryptor.decrypt_message(record[8].tobytes()), '%Y-%m-%d %H:%M:%S.%f'),
            "row_hash": record[9]
        }

    """
     @Notice: This function will update the event_type column from the table
     @Dev:    We first build the update query using the pub_key as key and update the event_type value
              regarding the status passed in parameter
    """
    def update_event_type(self, pubkey, status):
        query = "UPDATE data_store SET event_type = '" + self.encryptor.encrypt_message(status) + "' WHERE public_key = '" + pubkey + "'"
        self.db.execute(execution_string=query, commit=True)

    def insert_cron_record(self, cron_command, pubkey, filename, locked_period, scheduled_date):
        insert_query = """INSERT INTO cron_store(    
                            cron_command,
                            pubkey,
                            filename,
                            locked_period,
                            scheduled_date,
                            created,
                            row_hash) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        item_tuple = (
                    self.encryptor.encrypt_message(cron_command),
                    pubkey,
                    self.encryptor.encrypt_message(filename),
                    self.encryptor.encrypt_message(locked_period),
                    self.encryptor.encrypt_message(scheduled_date),
                    self.encryptor.encrypt_message(datetime.now()),
                    self.encryptor.hash_list([
                        pubkey,
                        filename,
                        locked_period]))
        self.db.execute(execution_string=insert_query, item_tuple=item_tuple, commit=True)

    """
     @Notice: This function will select from the database an item with the given parameters
     @Dev:    We first build our query using the row hash generate by the hash_list() function and then execute it with the tupple arguments
    """
    def select_by_row_hash(self, table_name: str, args_list: list):
        try:
            row_hash = self.encryptor.hash_list(args_list)
            query = """SELECT * FROM """ + table_name + \
                """ WHERE row_hash = '{row_hash}'""".format(row_hash=row_hash)
            return self.db.execute(execution_string=query, fetch_all=True)
        except Exception as e:
            raise e
        
    def update_is_excecuted_record(self, table_name, row_hash, value, encrypted=False):
        self.update_column(table_name, "is_executed", "row_hash", row_hash, value, encrypted)

    def update_column(self, table_name, column_name, id_name, id_value, col_value, encrypt=True):
        update_val = self.encryptor.encrypt_message(col_value)
        if encrypt is False:
            update_val = col_value
        query = "UPDATE " + table_name + " SET " + column_name + " = '" + str(update_val) + "' WHERE " + id_name + " = '" + str(id_value) + "'"
        self.db.execute(execution_string=query, commit=True)
        logging.info('column ' + column_name + ' updated with value ' + str(col_value) + ' for record ' + str(id_name) + " " + str(id_value) + ' on table ' + table_name)

    def is_cron_record(self, pubkey, filename, locked_period):
        query = "SELECT is_executed FROM cron_store WHERE row_hash = '" + self.encryptor.hash_list([pubkey, filename, locked_period]) + "'"
        cron = self.db.execute(execution_string=query, fetch_one=True)
        if cron is None or len(cron) == 0 or cron[0] is True:
            logging.warning('the cron does not exist in database or has already been executed')
            return False
        logging.info('the cron exists in database and has not already been executed')
        return True
    
    def insert_error(self, error, contract_address, name, raised_error):
        env = "test"
        if os.path.exists("/app") is True:
            env = "prod"
        item = self.select_by_row_hash("scripts_errors", [raised_error, contract_address, name, env])
        if len(item) == 0 or item[0][3] is True:
            insert_query = """INSERT INTO scripts_errors (error, contract_address, created, row_hash, name, env) VALUES (%s, %s, %s, %s, %s, %s)"""
            item_tuple = (self.encryptor.encrypt_message(error),
                        contract_address,
                        self.encryptor.encrypt_message(
                            str(datetime.now())),
                        self.encryptor.hash_list([raised_error, contract_address, name, env]),
                        self.encryptor.encrypt_message(name),
                        self.encryptor.encrypt_message(env))
            self.db.execute(execution_string=insert_query, item_tuple=item_tuple, commit=True)
            logging.info('error inserted to database')

    def get_investment_staking_id_by(self, pubkey):
        query = """SELECT staking_id FROM data_store WHERE public_key = '""" + str(pubkey) + """'"""
        item = self.db.execute(execution_string=query, fetch_one=True)
        if item is None or len(item) == 0:
            return None
        return item[0]
                
    def get_investment_address_by(self, staking_id):
        if staking_id is None:
            return None
        query = """SELECT contract_address FROM investment_store WHERE staking_id = '""" + str(staking_id) + """'"""
        item = self.db.execute(execution_string=query, fetch_one=True)
        if item is None or len(item) == 0:
            logging.warning("there isn't investment records in the database for this staking_id: " + str(staking_id))
            return None
        return item[0]