# goalposts
A way to keep my(your)self accountable.

### Requirements
* Python >=3.6
* python-myfitnesspal
* garminexport
* Internet connectivity

### Authentication
These services require authentication to be functional.

#### MyFitnessPal
After installing the project dependencies, run the following command to store your password in your system keyring:

```
$ myfitnesspal store-password <your MFP email>
```

#### Garmin
You need three pieces of information to get the Garmin connectivity to work, and this will hopefully be reduced in the future:
* Username
* Password
* User Token

### Configuration
Create `goalposts/config.py` and replace it with your information.

```python
MFP_USER = ''
GARMIN_USER = ''
GARMIN_PASS = r''
GARMIN_TOKEN = ''
REPORT_DIR = 'reports'
```

Also updated `goalposts/constants.py` with your target weight, current weight, and so on.


### Contact
justin@underlogic.io
