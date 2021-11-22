#!/bin/bash
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
echo "Deploy completed successfully"
