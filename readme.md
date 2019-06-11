## CloudVision API (rCVP API)

This is a custom CVP API wrapper.

### Support

This has been tested on CVP versions:
- 2018.2.2
- 2018.2.3
- 2018.2.4

### Usage

Install using the Python Package Index

```
pip install rcvpapi
```

Import into Python

```
from rcvpapi.rcvpapi import *

# Create connection to CloudVision
cvp_cnt = CVPCON(cvp_ip,cvp_user,cvp_user_pwd)

# Check current CloudVision session ID
cvp_cnt.SID

```