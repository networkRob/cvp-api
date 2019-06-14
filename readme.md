## CloudVision API (rCVP API)

This is a custom CVP API wrapper.

### Support

***NOTE*** Always test on lab deployments before working on a production environment.  Espeically between different releases of CVP and rCVP API.

This has been tested on CVP versions:
- 2018.2.2
- 2018.2.3
- 2018.2.4

### Usage

***NOTE***
The documentation below is incomplete and a work in progress.  This module has more functionality than what is documented.  With the right supplemental data and steps, it can configure CVP from nothing to functioning.

Install using the Python Package Index

```
pip install rcvpapi
```

#### Initial Setup and Usage

```
from rcvpapi.rcvpapi import *

# Create connection to CloudVision
cvp_cnt = CVPCON(cvp_ip,cvp_user,cvp_user_pwd)

# Check current CloudVision session ID
cvp_cnt.SID

# Get the current CVP Version
cvp_ver = cvp_cnt.checkVersion()

# Logout/End session
cvp_cnt.execLogout()

# Save topology
cvp_cnt.saveTopology()
```

#### Devices/Inventory
```
# Get all provisioned devices
cur_inv = cvp_cnt.getDeviceInventory()

# Adds new devices to inventory/provisioning
cvp_cnt.addDeviceInventory(['10.0.0.1','10.0.0.2'])
```

#### Tasks
```
# Get a list of any Task type
cur_tasks = cvp_cnt.getAllTasks("Pending")

# Execute all tasks
cvp_cnt.execAllTasks("Pending")

# Get status of a task
tsk_stat = cvp_cnt.getTaskStatus(task_id)
```

#### Configlets
```
# Import static configlet
cvp_cnt.impConfiglet("static",configlet_name,configlet_data)

# Import configlet builder
cvp_cnt.impCofniglet("builder",configlet_name,configlet_data,configlet_form_data)

# Get all Configlets
exist_configlets = cvp_cnt.getConfiglets()

# Get a Configlet by Name
ex_cfg = cvp_cnt.getConfigletByName("Base_Authentication")
```

#### Snapshots
```
# Get all configured snapshots
cvp_cnt.snapshots

# Add a new snapshot
# Parameters:
#        snap_name = Name of the snapshot (required)
#        snap_cmds = Array of all commands to be included in snapshot (required)
#        snap_devices = Array of any devices to be included on the snapshot (optional)
cvp_cnt.createSnapshot(snap_name,snap_cmds,snap_devices)
```

#### Containers
```
# Get all containers
ex_cont = cvp_cnt.getAllContainers()

# Add a new container
cvp_cnt.addContainer(new_cont_name,parent_cont_name)
```