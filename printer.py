from __future__ import print_function
import httplib2
import os


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

def gprinter(user_values, range_string):

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')

    #service = discovery.build('sheets', 'v4', http=http,  discoveryServiceUrl=discoveryUrl)
    service = discovery.build('sheets', 'v4', credentials=credentials)



    spreadsheetId = '1E_ZG6PEapGOo_rZqzKK4dUKwghQB2p0tjSlAF7zx7lE'
    '''rangeName = 'Schedule Data!A2:E'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()'''
    '''values = result.get('values', [])

    

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))'''


    # The A1 notation of the values to update.
    range_ = range_string  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'RAW'

    value_range_body = {"values": user_values}


    request = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    #pprint(response)




if __name__ == '__main__':
    main()