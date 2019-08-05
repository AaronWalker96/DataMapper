'''
Python script to refresh data from the Zendesk API.
Use me to update your existing data set.

Author: Aaron Walker
'''

# Imports
import os
import sys
from os import listdir
from os.path import isfile, join, exists
import requests
from requests.auth import HTTPBasicAuth
import fileinput
import json
import shutil


# Delete the folder and contents, recreate the foler
def folder_reset(folder):
    # Delete the folder and contents (if exists)
    if exists(folder):
        print(f'Removed {folder}')
        shutil.rmtree(folder)

    # Create the folder
    os.makedirs(folder)

    # Check if folder has been created
    if exists(folder):
        print(f'{folder} folder created')
    else:
        raise Exception(f'Failed to create {folder}')


# Make a get request to a URL and save the JSON
def get_data(url, json_loc):
    # Get credentials
    username,token = os.getenv("ZENDESK_USER"),os.getenv("ZENDESK_TOKEN")

    # Make API call
    print('Making API call...')
    r = requests.get(url, auth=(username, token))
    # Check response code
    if r.status_code == 401:
        raise Exception(f'API authentication error, have you specified the correct auth token?')
    elif r.status_code != 200:
        raise Exception(f'API response error, return code: {r.status_code}')

    # Save response to file
    with open(json_loc, 'w') as f:
        f.write(str(r.text))
        print(f'Results saved to: {json_loc}')

    return r


# Get the file with the highest number in the name
def get_most_recent(folder):
    # Get list of files in folder
    file_list = [f for f in listdir(folder) if isfile(join(folder, f))]
    max_val,cur_val = 0,0

    # Get the largest numbered file
    for json_file in file_list:
        json_file = json_file[:-5]  # Remove the '.json' file extension
        cur_val = [int(s) for s in json_file.split('_') if s.isdigit()][0]  # Get number from file name
        if cur_val > max_val:
            max_val = cur_val

    return max_val


# Get new tickets
def get_new_tickets(folder):
    next_page = True

    # Get latest tickets json file
    most_recent = get_most_recent('tickets') # Get the 'page' number from the most recent file
    page_count = most_recent

    # Continue to call the API while a next page is available
    while next_page:
        # Make API call
        url = f'https://transformsupport.zendesk.com/api/v2/tickets.json?page={page_count}'
        output_file = join(folder, f'tickets_{page_count}.json')
        r = get_data(url, output_file)

        # Are there more pages?
        data = r.content
        data_unpacked = json.loads(data)
        if data_unpacked['next_page'] is None:
            next_page = False

        # Get the next page
        page_count += 1
    
    return most_recent


# Get new ticket audits
def get_new_ticket_audits(folder, url):
    # Get cursor to read from
    recent_file_count = get_most_recent('ticket_audits') - 1
    recent_file = f'{folder}/ticket_audits_{recent_file_count}.json'
    print(f'most recent file: {recent_file}')
    with open(recent_file, 'r') as f:
        datastore = json.load(f)
        cursor = datastore['before_cursor']

    page_count = recent_file_count
    next_page = True

    # Continue to call the API while a next page is available
    while next_page:
        # Make API call
        cur_url = url + f'?cursor={cursor}'
        print(f'Calling {cur_url}')
        output_file = join(folder, f'ticket_audits_{page_count}.json')
        r = get_data(cur_url, output_file)

        # Are there more pages?
        data = r.content
        data_unpacked = json.loads(data)
        cursor = data_unpacked['before_cursor']
        if cursor is None:
            next_page = False

        # Get the next page
        page_count += 1
    
    return recent_file_count


# Combine new data with existing JSON - TO COMPLETE
def update_json(folder, combine_from, json_object):
    # Get the files
    print('Beginning the much... nom nom nom')

    # Add each file to the results file
    while os.path.exists(f'folder/ticket_audits_{combine_from}.json'):
        with open(join(folder, f'ticket_audits_{combine_from}.json'), 'r') as tickets:
            content = json.loads(tickets.read())
            with open('data', 'a+') as result:
                json.dump(content[json_object], result)
        combine_from += 1

    # Remove the joins of the json objects
    print('Completed file combining, formatting results file...')
    with fileinput.FileInput('data', inplace=True,) as f:
        for line in f:
            print(line.replace('][', ','), end='')


def main():
    # Delete and recreate folders of 'easy to pull' scripts
    folder_reset('data')

    # Update existing data and format
    get_data('https://transformsupport.zendesk.com/api/v2/users.json', 'data/users.json')
    get_data('https://transformsupport.zendesk.com/api/v2/business_hours/schedules.json', 'data/business_hours.json')
    ticket_count = get_new_tickets('tickets')
    #update_json('tickets', ticket_count, 'tickets')
    audit_count = get_new_ticket_audits('ticket_audits', 'https://transformsupport.zendesk.com/api/v2/ticket_audits.json')
    #update_json('ticket_audits', audit_count, 'audits')


if __name__ == "__main__":
    main()
