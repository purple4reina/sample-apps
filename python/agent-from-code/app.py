#!/usr/bin/env python

# This script is run on cron once per day
#
# If there is a weather advisory for the given US state, then post the advisory
# in slack and send an email to the administrators.

#######################
# 1. INITIALIZE AGENT #
#######################

import ddtrace
ddtrace.patch_all()

import datadog_agent
datadog_agent.init()

import requests
import emails
import slack

STATE = 'OR'
ADMIN_EMAILS = 'rey.abolofia@datadoghq.com'
SLACK_CHANNEL = '#weather-advisories'

######################
# 2. WRAP ENTRYPOINT #
######################

@datadog_agent.wrap
def main(event):
    state = 'OR'
    advisories = get_weather_advisories()
    if advisories:
        advisories_txt = format_advisories(advisories)
        email_admin(advisories_txt)
        post_to_slack(advisories_txt)

_weather_advisories_url = f'https://api.weather.gov/alerts/active?area={STATE}'
def get_weather_advisories():
    resp = requests.get(_weather_advisories_url)
    resp.raise_for_status()
    return resp.json()['features']

def format_advisories(advisories):
    adv_txts = '\n'.join(
            f'  ADVISORY: {a["properties"]["event"]} in {a["properties"]["areaDesc"]}'
            for a in advisories
    )
    return f'Weather advisories found for {STATE}:\n{adv_txts}'

_email_from = 'weather.admin@datadoghq.com'
_email_subject = 'Weather advisories'
def email_admin(advisories):
    emails.send_email(ADMIN_EMAILS, _email_from, _email_subject, advisories)

def post_to_slack(advisories):
    slack.post_to_channel(advisories, SLACK_CHANNEL)

if __name__ == '__main__':
    main({})
