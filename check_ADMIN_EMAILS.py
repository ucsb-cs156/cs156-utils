#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check dokku deployments for ADMIN_EMAILS config variables
"""

import argparse

def read_csv(csv_file):
    # read the CSV file and return a dictionary with githubid as the key and a dictionary of the other fields as the values
    import csv
    data = {}
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            githubid = row['GITHUBLOGIN']
            data[githubid] = row
    return data

DEBUG = False

def get_dokku_appname(dokku_appname_prefix, githubid):
    return f"{dokku_appname_prefix}-{githubid}"

def get_dokku_hostname(student_dict, githubid):
    team = student_dict[githubid]['TEAMS']
    # Team number is last two characters of team string
    team_suffix = team[-2:]
    return f"dokku-{team_suffix}.cs.ucsb.edu"
    

def email_csv_string_to_staff_email_set(staff_emails):
    return set([email.strip() for email in staff_emails.split(',')])

def get_team_to_admin_emails(student_dict, staff_emails):
    staff_email_set = email_csv_string_to_staff_email_set(staff_emails)
    team_to_admin_emails = {}
    for student_info in student_dict.values():
        team = student_info['TEAMS']
        email = student_info['EMAIL']
        if team not in team_to_admin_emails:
            team_to_admin_emails[team] = { email }  
        else:
            team_to_admin_emails[team].add(email)  
    for team, emails in team_to_admin_emails.items():
        team_to_admin_emails[team] = emails.union(staff_email_set)
    return team_to_admin_emails
    
def add_admin_email_set_to_student_dict_entries(student_dict, staff_emails):
    team_to_admin_emails = get_team_to_admin_emails(student_dict, staff_emails)
    for k, v in student_dict.items():
        student_dict[k]['admin_email_set'] = team_to_admin_emails[v['TEAMS']]    
    return student_dict

def return_matching_lines(output, prefix):
    DEBUG and print(f"Looking for lines starting with '{prefix}' in output:\n{output}")
    return [line for line in output.splitlines() if line.startswith(prefix)]

def convert_admin_emails_line_to_set(admin_emails_line):
    if not admin_emails_line:
        return None
    admin_emails_value = admin_emails_line.split(':', 1)[1].strip().strip('"')
    return set(email.strip() for email in admin_emails_value.split(','))

def check_dokku_apps(student_dict, dokku_appname_prefix):
    import subprocess
    for githubid, student_info in student_dict.items():
        dokku_appname = get_dokku_appname(dokku_appname_prefix, githubid)
        try:
            dokku_host = get_dokku_hostname(student_dict, githubid)
            DEBUG and print(f"Checking {dokku_appname} on {dokku_host}")
            result = subprocess.run(['ssh', dokku_host, 'dokku', 'config:show', dokku_appname], capture_output=True, text=True, check=True)
            config_output = result.stdout
            DEBUG and print(f"Config output for {dokku_appname}:\n{config_output}")
            admin_emails_line = return_matching_lines(config_output, 'ADMIN_EMAILS:')[0] if return_matching_lines(config_output, 'ADMIN_EMAILS:') else None
            admin_emails_set = convert_admin_emails_line_to_set(admin_emails_line)
            if admin_emails_set is not None:
                expected_admin_email_set = student_info['admin_email_set']
                if admin_emails_set == expected_admin_email_set:
                    print(f"{dokku_appname}: ADMIN_EMAILS is correct.")
                else:
                    print(f"{dokku_appname}: ADMIN_EMAILS is INCORRECT.")
                    print(f"  Expected: {expected_admin_email_set}")
                    print(f"  Found:    {admin_emails_set}")
            else:
                print(f"{dokku_appname}: ADMIN_EMAILS not found in config.")
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving config for {dokku_appname}: {e}")


def main():
    
    ### PARSE ARGUMENTS ###
    
    import argparse
    parser = argparse.ArgumentParser()
    # Add an argument for the CSV file from frontiers
    parser.add_argument('csv_file', help='Path to the CSV file from frontiers')
    # Add an argument for the dokku appname prefix
    parser.add_argument('dokku_appname_prefix', help='Prefix for dokku app names (will be followed by hyphen and githubid)')
    # Add an argument for the staff email address
    parser.add_argument('staff_emails', help='Staff email address to check for in ADMIN_EMAILS')
    # Add a debug flag, default false
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    global DEBUG
    parser.set_defaults(debug=False)
    DEBUG = parser.parse_args().debug
    
    args = parser.parse_args()

    ### PARSE THE INPUT AND PREPARE THE DICTIONARY ###
    
    student_dict = read_csv(args.csv_file)
    student_dict = add_admin_email_set_to_student_dict_entries(student_dict, args.staff_emails)

    ### CHECK THE DOKKU APPS ###

    check_dokku_apps(student_dict, args.dokku_appname_prefix)


if __name__ == "__main__":
    main()

