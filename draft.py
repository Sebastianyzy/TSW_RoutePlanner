import requests
import smtplib


api_file_name = ""
#API key
api_file = open(api_file_name, "r")
api_key = api_file.read()
api_file.close()

