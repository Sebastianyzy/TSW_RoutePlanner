import requests
import smtplib


api_file_name = "api.txt"
#API key
api_file = open(api_file_name, "r")
api_key = api_file.read()
print(api_key)
api_file.close()


# home address input 
