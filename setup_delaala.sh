#!/bin/bash

# Set required environment variables for development
export SECRET_KEY='django-insecure-development-key-for-setup'
export DEBUG='1'
export ALLOWED_HOSTS='localhost,127.0.0.1,delaala.co.uk'
export CSRF_TRUSTED_ORIGINS='https://delaala.co.uk'

# Run the setup command
"/Users/gideonowusu/Desktop/Learn Django/Schedulo/env/bin/python" manage.py setup_tenant \
  --name "Delaala Company Limited" \
  --domain "delaala.co.uk" \
  --email "noreply@delaala.co.uk" \
  --display-name "Delaala Company"
