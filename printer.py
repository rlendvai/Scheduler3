from __future__ import print_function
import httplib2
import os
import config
import pendulum

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pprint import pprint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def gprinter(user_values, range_string, operation = None, insert_column_first=None, insert_column_last=None):



    credentials = get_credentials()

    service = discovery.build('sheets', 'v4', credentials=credentials)

    spreadsheetId = '1E_ZG6PEapGOo_rZqzKK4dUKwghQB2p0tjSlAF7zx7lE'

    if operation == 'clear':
        requests=[]
        request = {"updateCells": {
                            "range": {
                                "sheetId" : 0
                            },
                            "fields": "userEnteredValue"
                             }
                        }

        requests.append(request)
        body = {'requests': requests}
        request_response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()
        LOG.log(request_response, 'logging')

        return

    if operation == "insert":
        requests = []
        if operation == 'insert':
            request = {"insertDimension": {
                                                    "range": {
                                                            "dimension": "COLUMNS",
                                                            "startIndex": insert_column_first,
                                                            "endIndex": insert_column_last+1
                                                    }
                                                 }
                              }
            requests.append(request)
            body = {'requests': requests}
            insert_response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()
            LOG.log(insert_response, 'logging')

    # The A1 notation of the values to update.
    range_ = range_string
    value_input_option = 'RAW'
    value_range_body = {"values": user_values}
    LOG.log("Google printing", 'logging')


    request = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, body=value_range_body)
    write_response = request.execute()

    # TODO: Change code below to process the `response` dict:

    LOG.log(write_response, 'logging')
    #pprint(write_response)


#
def gcolumn_printer(values, columns_to_move):
    pass

class Log:
    def __init__(self):
        self.log_lines = []
        self.log_range = config.log_range
        self.first_grow = config.total_entries + 2
        self.current_grow = self.first_grow
        self.schedule_has_been_printed_before = False

    def log(self, event_string, type='general'):

        assert type in config.event_print_types , "Trying to log unknown type."

        line={'time' : pendulum.now(), 'event' : event_string, 'type' : type}
        self.log_lines.append(line)

        self.print_log_line(line)


    #expects a dict(line) which contains a string, a line type, and a time
    def print_log_line(self, line):
        event_type = line['type']
        print_type = config.event_print_types[event_type]
        if 'console' in print_type:
            print(line['event'])
        elif 'google' in print_type:
            range_string = "B" + str(self.current_grow) + ":B" + str(self.current_grow)
            gprinter(line['event'], range_string)
            self.current_grow += 1

    def gprint_log(self, verbose = False, everything = True):

        values = []
        counter = 0
        for line in reversed(self.log_lines):
            if verbose is True or line['always_show'] is True:
                values.append([line['time'].isoformat(), line['event']])
            counter += 1
            if not everything and counter == self.num_lines_to_show:
                    break

        LOG.log("Printing complete log...", 'logging')
        g_range = self.log_range
        values = list(reversed(values))


        gprinter(values, g_range)

    def scheduleDisplay(self, entries):

        #Printing the schedule the first time is special - we print the times of day. In other iterations we don't.

        if 'console' in config.event_print_types['schedule']:
            print('\n')
            current_day = None
            for entry in entries:
                if current_day != entry[0].split(' ', 1)[0]:
                    print("------")
                    current_day = entry[0].split(' ', 1)[0]
                print(entry[0], entry[1]  )
            print('\n')

        if 'google' in config.event_print_types['schedule']:
            if self.schedule_has_been_printed_before is False:
                self.schedule_has_been_printed_before = True
                operation = None
                #Since it's the first column, with the time entries, it's not an insert
                insert_column_first = None
                insert_column_last = None
                range = config.schedule_display_range_initial
            else:
                just_patients = []
                for entry in entries:
                    just_patients.append([entry[1]])
                entries = just_patients
                operation = "insert"
                insert_column_first = 1
                insert_column_last = 1
                range = config.schedule_display_range_secondary

            gprinter(entries, range, operation = operation, insert_column_first=insert_column_first, insert_column_last=insert_column_last)
            # Reset the current log printing row to the top, since we just started a new column.
            # We are printing log lines below each day's schedule, this is how we keep track of where the
            # 'bottom' of the schedule is.
            self.current_grow = self.first_grow

LOG = Log()
