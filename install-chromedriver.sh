#!/bin/bash

##
# Script to install chromedrive dependency:
# - It assumes your venv is named venv
# - First make the script executable. Maybe `$ chmod +x install-chromedriver.sh`
# - Then you likely need to update the permission for chromedriver. e.g.
#   `$ chmod 755 venv/bin/chromedriver`
## 

source venv/bin/activate
PLATFORM=mac64
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip \
| bsdtar -xvf - -C venv/bin/
