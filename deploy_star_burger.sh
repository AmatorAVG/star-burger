#!/bin/bash
set -e
set -o pipefail
git pull
source env/bin/activate
pip install -r requirements.txt
apt install nodejs --yes
npm install --include=dev
npm install -g parcel@latest
npm add @babel/runtime
parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
systemctl reload nginx.service
systemctl restart starburger.service

ACCESS_TOKEN=`cat .env | grep ACCESS_TOKEN= | cut -d '=' -f2`
ENVIRONMENT=production
LOCAL_USERNAME=root
REVISION=`git rev-parse --verify HEAD`
curl https://api.rollbar.com/api/1/deploy/ -F access_token=$ACCESS_TOKEN -F environment=$ENVIRONMENT -F revision=$REVISION -F local_username=$LOCAL_USERNAME

echo "Deploy completed successfully"
