#!/usr/bin/python3

# check my DL eligibility

# Your DL number
DLNUM = "01234567"
# Your DOB
DOB = [4, 1, 1969]
# Last 4 of your SSN
SSN = 0123

import requests

headers = {
    'Referer': 'https://txapps.texas.gov/txapp/txdps/dleligibility/login.do'
}
formdata = {
    #'XXtask': '1',
    'dlId': DLNUM,
    'dob': '{:02d}/{:02d}/{:04d}'.format(DOB[0], DOB[1], DOB[2]),
    'last4ssn': '{:04d}'.format(SSN)
}
r = requests.post('https://txapps.texas.gov/txapp/txdps/dleligibility/login.do', data=formdata, headers=headers)


#print(r.headers)
#print(r.text)

if not "You have outstanding citations under the Failure to Appear/Failure to Pay Program." in r.text:
    print("free and clear")
#else:
    #print("not yet")
