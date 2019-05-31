## CloudVision API (rCVP API)

This is a custom CVP API wrapper.

### Support

This has been tested on CVP versions:
- 2018.2.2
- 2018.2.3
- 2018.2.4

### Usage

Download the updated release from `release/` and install

```
pip install rcvp_api-1.0-py2-non-any.whl
```

Import into Python

```
from rcvp_api.rcvpapi import *

# Create connection to CloudVision
cvp_cnt = CVPCON(cvp_ip,cvp_user,cvp_user_pwd)

# Check current CloudVision session ID
cvp_cnt.SID

```