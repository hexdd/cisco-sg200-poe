#!/usr/bin/python3

import argparse
import math
import requests
import pickle

class CiscoSwitch:
    def __init__(self, hostname, username, password):
        self.hostname = 'http://' + hostname
        self.username = username
        self.pwd2 = self.final_encode(password)
        if verbose: print('encoded password (pwd2) is', self.pwd2)
            
    def login(self):
        self.session = requests.session()
        data = { 'uname': self.username, 'pwd2': self.pwd2 }
        url = self.hostname + '/nikola_login.html'
        try:
            r = self.session.post(url, data, allow_redirects=False, timeout=3)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e.args[0])
            return True;
        except requests.exceptions.RequestException as e:
            print("Error Connecting")
            if verbose: print(e)
            return True
        
        return False;
    
    def poe_enable(self, port, enable):
        if self.login():
            return True;
        
        portstr = 'g' + str(port)
        command = 'Enable' if enable == 1 else 'Disable'
        data = {
            'v_1_1_1': '1',
            'v_1_2_1': portstr,
            'v_1_2_1': portstr,
            'v_1_3_2': command,
            'v_1_16_1': 'Apply',
            'submit_flag': '8',
            'submit_target': 'EditPoESettingsPortLimit.html',
            'err_flag': '0',
            'err_msg': '',
            'dbgopt': '0',
        }
            
        url = self.hostname + '/EditPoESettingsPortLimit.html/a1'
        try:
            r = self.session.post(url, data, allow_redirects=False, timeout=3)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e.args[0])
            return True;
        except requests.exceptions.RequestException as e:
            print ("Error Connecting")
            if verbose: print(e)
            return True

        if r.status_code == 302:
            print('Error: login attempt failed')
            return True;
        
        return False;
        
    def init_encode(self, inputVal):
        inputVal = inputVal.replace('\r\n', '\n');
        outVal = '';
        
        for n in range(len(inputVal)):
            c = inputVal[n]
            if ord(c) < 128:
                outVal += chr(ord(c))
            elif ((ord(c) > 127) and (ord(c) < 2048)):
                outVal += chr((ord(c) >> 6) | 192)
                outVal += chr((ord(c) & 63) | 128)
            else:
                outVal += chr((ord(c) >> 12) | 224);
                outVal += chr(((ord(c) >> 6) & 63) | 128);
                outVal += chr((ord(c) & 63) | 128);
        
        return outVal;
  
    def final_encode(self, inputVal):
        output = ''
        i = 0
        keyVal='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
        inputVal = self.init_encode(inputVal)
        
        while (i < len(inputVal)):
            c1 = inputVal[i]
            i = i + 1
            
            if (i < len(inputVal)):
                c2 = inputVal[i]
            else:
                c2 = '\0'
            i = i + 1
            
            if (i < len(inputVal)):
                c3 = inputVal[i]
            else:
                c3 = '\0'
            i = i + 1
            
            x1 = ord(c1) >> 2
            x2 = ((ord(c1) & 3) << 4) | (ord(c2) >> 4)
            x3 = ((ord(c2) & 15) << 2) | (ord(c3) >> 6)
            x4 = ord(c3) & 63

            if (i >= len(inputVal) + 2):
                x3 = x4 = 64
            elif (i >= len(inputVal) + 1):
                x4 = 64
                
            output = output + keyVal[x1] + keyVal[x2] + \
                keyVal[x3] + keyVal[x4]
                
        return output
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enable/Disable PoE on Cisco Switch')
    
    parser.add_argument('-H', '--hostname', type=str, nargs=1, required=True,
            help='remote server hostname or IP address')
    parser.add_argument('-u', '--username', type=str, nargs=1, required=True,
            help='login username')
    parser.add_argument('-p', '--password', type=str, nargs=1, required=True,
            help='login password')

    parser.add_argument('-P', '--port', type=int, nargs=1, required=True,
            help='port number', choices=range(1, 5))
    parser.add_argument('-e', '--enable', type=int, nargs=1, required=True,
            help='enable or disable PoE', choices=range(0, 2))

    parser.add_argument('-v', '--verbose', action='store_true',
            help='enable verbose output')

    try:
        args = parser.parse_args()
    except:
        exit(1)
    
    verbose = args.verbose
    if verbose:
        print('Accessing host', args.hostname[0]);
    
    cisco = CiscoSwitch(args.hostname[0], args.username[0], args.password[0])
    result = cisco.poe_enable(port=args.port[0], enable=args.enable[0]);
    if result:
        print('Unable to perform action')
    else:
        print('Successfully modified switch parameter')
