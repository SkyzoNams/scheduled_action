# Introduction 
<p>This repository group two python scripts. One is for creating a cron to execute the other.</p>
<p>The cron_creator script will be executed threw an api and will create a cron to execute the second script. The cron will be parameted to be executed at the end of the staking period in order to exit the node from the validator.</p>
<p>The scheduled_action_executer script will be executed by the cron at the end of the staking period. It will first make sure the cron is valid and the period over, then execute the node api endpoint to exit the node, update the staking status and finally disable the cron.</p>

# 0ffchain scrips
1. [event_listener](https://github.com/SkyzoNams/event_listener)
2. [records_handler](https://github.com/SkyzoNams/records_handler)
3. [key_generation](https://github.com/SkyzoNams/key_generation)
4. [scheduled_action](https://github.com/SkyzoNams/scheduled_action)
5. [keys_handler](https://github.com/SkyzoNams/keys_handler)

# Getting Started
1.	Clone the repo
2.  Make sure to have Python 3 installed on your machine (developed with Python 3.7.8)
3.  Go inside the project root you want to execute (/event_listener)
4.  Create your local venv by doing "python3 -m venv ./venv"
5.  Activate the venv by doing "source venv/bin/activate"
6.	From the project rool install all the dependencies by doing "pip install -r requirements.txt"
