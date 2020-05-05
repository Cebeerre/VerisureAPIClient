#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import xmltodict
from datetime import datetime
import time
import json
import argparse
import textwrap
import itertools


class VerisureAPIClient():
    BASE_URL = 'https://mob2217.securitasdirect.es:12010/WebService/ws.do'
    DALARM_OPS = {
        'ARM': 'arm all sensors (inside)',
        'ARMDAY': 'arm in day mode (inside)',
        'ARMNIGHT': 'arm in night mode (inside)',
        'PERI': 'arm (only) the perimeter sensors',
        'DARM': 'disarm everything (not the annex)',
        'ARMANNEX': 'arm the secondary alarm',
        'DARMANNEX': 'disarm the secondary alarm',
        'EST': 'return the panel status'
    }
    DAPI_OPS = {
        'ACT_V2': 'get the activity log',
        'SRV': 'SIM Number and INSTIBS',
        'MYINSTALLATION': 'Sensor IDs and other info'
    }
    PANEL = 'SDVFAST'
    TIMEFILTER = '3'
    RATELIMIT = 1
    ALARM_OPS = list(DALARM_OPS.keys())
    API_OPS = list(DAPI_OPS.keys())

    def __init__(self, **args):
        self.user = args.get('username')
        self.LOGIN_PAYLOAD = {'Country': args.get('country'),
                              'user': args.get('username'), 'pwd': args.get('password'), 'lang': args.get('language')}
        self.OP_PAYLOAD = {'Country': args.get('country'), 'user': args.get('username'),
                           'pwd': args.get('password'), 'lang': args.get('language'), 'panel': self.PANEL, 'numinst': args.get('installation')}
        self.OUT_PAYLOAD = {'Country': args.get('country'), 'user': args.get('username'),
                            'pwd': args.get('password'), 'lang': args.get('language'), 'numinst': '(null)'}

    def return_commands(self):
        all_ops = dict(itertools.chain(
            self.DALARM_OPS.items(), self.DAPI_OPS.items()))
        return all_ops

    def call_verisure_get(self, method, parameters):
        time.sleep(self.RATELIMIT)
        if method == 'GET':
            response = requests.get(self.BASE_URL, params=parameters)
        elif method == 'POST':
            response = requests.post(self.BASE_URL, params=parameters)
        if response.status_code == 200:
            output = xmltodict.parse(response.text)
            return output
        else:
            return None

    def op_verisure(self, action, hash, id):
        payload = self.OP_PAYLOAD
        payload.update({'request': action, 'hash': hash, 'ID': id})
        if action in self.ALARM_OPS:
            payload['request'] = action + '1'
            self.call_verisure_get('GET', payload)
            payload['request'] = action + '2'
            output = self.call_verisure_get('GET', payload)
            res = output['PET']['RES']
            while res != 'OK':
                output = self.call_verisure_get('GET', payload)
                res = output['PET']['RES']
        elif action in self.API_OPS:
            if action == 'ACT_V2':
                payload.update(
                    {'timefilter': self.TIMEFILTER, 'activityfilter': '0'})
            output = self.call_verisure_get('GET', payload)
        clean_output = output['PET']
        del clean_output['BLOQ']
        return clean_output

    def generate_id(self):
        ID = 'IPH_________________________' + self.user + \
            datetime.now().strftime("%Y%m%d%H%M%S")
        return ID

    def get_login_hash(self):
        payload = self.LOGIN_PAYLOAD
        payload.update({'request': 'LOGIN', 'ID': self.generate_id()})
        output = self.call_verisure_get('POST', payload)
        return output['PET']['HASH']

    def logout(self, hash):
        payload = self.OUT_PAYLOAD
        payload.update({'request': 'CLS', 'hash': hash,
                        'ID': self.generate_id()})
        output = self.call_verisure_get('GET', payload)
        return None

    def operate_alarm(self, action):
        if (action in self.ALARM_OPS) or (action in self.API_OPS):
            try:
                hash = self.get_login_hash()
                id = self.generate_id()
                status = self.op_verisure(action, hash, id)
                self.logout(hash)
                return status
            except:
                output = { 'RES':'ERROR', 'MSG':'Something went wrong. Check your credentials and/or the installation ID' }
                return output


def create_args_parser(help_cmd):
    desc = 'Verisure/SecuritasDirect API Client\nhttps://github.com/Cebeerre/VerisureAPIClient'
    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u',
                        '--username',
                        help='Username used in the web page/mobile app.',
                        required=True)
    parser.add_argument('-p',
                        '--password',
                        help='Password used in the web page/mobile app.',
                        required=True)
    parser.add_argument('-i',
                        '--installation',
                        help='Installation/Facility number (appears on the website).',
                        required=True)
    parser.add_argument('-c',
                        '--country',
                        help='Your country (UPPERCASE): ES, IT, FR, GB, PT ...',
                        required=True)
    parser.add_argument('-l',
                        '--language',
                        help='Your language (lowercase): es, it, fr, en, pt ...',
                        required=True)
    parser.add_argument('COMMAND',
                        help=textwrap.dedent(help_cmd),
                        type=str)
    return parser


def main():
    commands = VerisureAPIClient().return_commands()
    help_commands = '\n'.join([': '.join(i) for i in commands.items()])
    args = create_args_parser(help_commands).parse_args()
    initparams = vars(args)
    client = VerisureAPIClient(**initparams)
    output=client.operate_alarm(args.COMMAND)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
