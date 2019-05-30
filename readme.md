## CloudVision API (rCVP API)

This is a custom CVP API wrapper.

### Usage

Download the updated release from `release/` and install

```
pip install rcvp_api-1.0-py2-non-any.whl
```

Import into Python

```
from rcvp_api import rcvpapi

# Create connection to CloudVision
cvp_cnt = rcvpapi.CVPCON(cvp_ip,cvp_user,cvp_user_pwd)

# Check current CloudVision session ID
cvp_cnt.SID

```