import requests
import json
import urllib
import urllib.parse
from urllib.parse import quote
from selenium import webdriver
import time


# Motive Token
TOKEN = "Token.txt"
TSW_TOKEN = "TSW_Token.txt"
PROFILE_PATH = "chrome_profile.txt"
api_prefix = "https://api.keeptruckin.com/api/i1/dispatch_share?token="
api_user = "https://api.keeptruckin.com/v1/users/"
api_message = "https://api.keeptruckin.com/v1/messages?"
api_role = "https://api.keeptruckin.com/v1/users?"
googlemap_prefix = "www.google.com/maps/dir"


# use this function to get token and admin id, do not push the txt files to git


def get_file_content(file):
    try:
        file = open(file, "r")
        content = file.read()
        file.close()
    except:
        print("\nError! Unable to get file: {}\n".format(file))
    return content

# concatenate the googlemap link with all the locations in trip list


def generate_route_plan(gm_prefix, trip):
    i = 0
    temp = gm_prefix
    while i < len(trip):
        temp += '/{}'.format(trip[i].replace(" ", "+"))
        i += 1
    # url format are different in motive's text editor and python terminal
    url = "https://{}".format(urllib.parse.quote(temp))
    return url

# extract token from a link


def generate_api_link(url):
    splitted = ""
    try:
        splitted = url.split("token=")
    except:
        print("\nError! Unable to extract token from link: \n{}".format(url))
    return api_prefix+splitted[1]


def load_trip(motive_link):
    trip = []
    order_number = "unknown order_number"
    first_stop = "unknown"
    last_stop = "unknown"
    num_of_stops = "unknown"
    # If loading trip fails, we set STATUS to false and return back to main()
    STATUS = True
    try:
        headers = {'X-Internal-Api-Key': get_file_content(TOKEN)}  # TOKEN
        data = requests.get(generate_api_link(motive_link), headers=headers)
        data = data.text
        # use a list to store all addresses
        parse_json = json.loads(data)
        # company name
        company = parse_json["dispatch"]["company"]["name"]
        # last stop before heading back
        consignee_dispatch_location = parse_json["dispatch"]["consignee_dispatch_location"]
        # first stop
        shipper_dispatch_location = parse_json["dispatch"]["shipper_dispatch_location"]
        # the rest of the stops
        dispatch_stops = parse_json["dispatch"]["dispatch_stops"]

        consignee = consignee_dispatch_location["address1"]+", "+consignee_dispatch_location["city"]+", " + \
            consignee_dispatch_location["state"]+" "+consignee_dispatch_location["zip"] + \
            ", " + consignee_dispatch_location["country"]
        shipper = shipper_dispatch_location["address1"]+", "+shipper_dispatch_location["city"]+", " + \
            shipper_dispatch_location["state"]+" "+shipper_dispatch_location["zip"] + \
            ", " + shipper_dispatch_location["country"]
        first_stop = "{}, {}".format(
            shipper_dispatch_location["city"], shipper_dispatch_location["state"])
        last_stop = "{}, {}".format(
            consignee_dispatch_location["city"], consignee_dispatch_location["state"])
        # add company's address as the origin
        trip.append(company)
        # add shipper(the second stop) address, this is how the location data is being stored in the GoMotive database
        trip.append(shipper)
        # create a hash map to sort the stops
        hash_map = {}
        i = 0
        while i < len(dispatch_stops):
            stops_number = dispatch_stops[i]["dispatch_stop"]["number"]
            dispatch_parse = dispatch_stops[i]["dispatch_stop"]["dispatch_location"]
            customer_address = dispatch_parse["address1"]
            customer_city = dispatch_parse["city"]
            customer_province = dispatch_parse["state"]
            customer_zip = dispatch_parse["zip"]
            customer_country = dispatch_parse["country"]
            address_to_append = customer_address+", "+customer_city+", " + \
                customer_province+" "+customer_zip + ", " + customer_country
            hash_map[stops_number] = address_to_append
            i += 1
        # sotre the sorted stops into trip
        for v in sorted(hash_map.keys()):
            trip.append(hash_map[v])
        # last stop before heading back
        trip.append(consignee)
        # final destination is the origin
        trip.append(company)
        # order_number on GoMotive is the date data
        order_number = parse_json["dispatch"]["order_number"]
        num_of_stops = len(trip)-2
    except:
        STATUS = False
        print("\nError! Unable to load trip!\n")
    return trip, order_number, first_stop, last_stop, num_of_stops, STATUS


def get_driver_id_from_dispatch_instance(url, TOKEN):
    driver_id = "unknown"
    try:
        headers = {'X-Internal-Api-Key': get_file_content(TOKEN)}
        data = requests.get(generate_api_link(url), headers=headers)
        data = data.text
        parse_json = json.loads(data)
        driver_id = parse_json["dispatch"]["form_entries"][0]["form_entry"]["driver_id"]
    except:
        print("\nError! Unable to get the driver's id! \n")
    return str(driver_id)

# return the user's name


def get_user_name(user_id, TOKEN):
    user_name = "anonymous"
    try:
        headers = {
            "accept": "application/json",
            "X-Api-Key": get_file_content(TOKEN)
        }
        data = requests.get(api_user+user_id, headers=headers)
        data = data.text
        parse_json = json.loads(data)
        user_name = parse_json["user"]["first_name"] + \
            " "+parse_json["user"]["last_name"]
    except:
        print("\nError! Unable to get user's name! ")
    return str(user_name)

# return a list which contain all members with the same role


def get_role_list(role, per_page, page_no, TOKEN):
    role_list = []
    try:
        url = "{}role={}&per_page={}&page_no={}".format(
            api_role, role, per_page, page_no)
        headers = {
            "accept": "application/json",
            "X-Api-Key": get_file_content(TOKEN)
        }
        data = requests.get(url, headers=headers)
        data = data.text
        parse_json = json.loads(data)
        i = 0
        while i < len(parse_json["users"]):
            role_list.append(str(parse_json["users"][i]["user"]["id"]))
            i += 1
    except:
        print("\nError! Unable to get {} list!".format(role))
    return role_list


def send_message(recipient_id, message_body, TOKEN):
    url = ""
    url = "{}recipient_id={}&body={}".format(
        api_message, str(recipient_id), message_body)
    headers = {
        "accept": "application/json",
        "X-Api-Key": get_file_content(TOKEN),
    }
    response = requests.post(url, headers=headers)
    if response.status_code >= 300:
        print("\nMessage failed to deliver!\n{}\n{}\n".format(
            response, response.text, response.reason))
    else:
        print("\nMessage Sent!\n")
    return


def main():
    try:
        motive_link = input("\n\nEnter copied dispatch url: ")

        print("\nrunning...\n\n")
        trip, order_number, first_stop, last_stop, num_of_stops, STATUS = load_trip(
            motive_link)
        url = generate_route_plan(googlemap_prefix, trip)
        driver_id = get_driver_id_from_dispatch_instance(motive_link, TOKEN)
        driver_name = get_user_name(driver_id, TSW_TOKEN)

        if STATUS:
            # get all the admin_id
            ADMINS = get_role_list("admin", 25, 1, TSW_TOKEN)
            PATH = get_file_content(PROFILE_PATH)
            driver = webdriver.Chrome(executable_path=PATH)
            driver.get(url)
            time.sleep(5)
            url_to_send = driver.current_url
            driver.close()
            message_to_admin = "\nThe Following Message Was Sent To: {} (id: {})\n--------------------------------------------------------------\n".format(
                driver_name, driver_id)
            message_info = "Google Map Route Plan\n{} --> {} ({} stops)\n\ndate: {}\ndriver: {}\n\n".format(
                first_stop, last_stop, num_of_stops, order_number, driver_name)
            # send message to driver
            message_body = message_info+quote(url_to_send)
            send_message(driver_id, message_body, TSW_TOKEN)
            # send a copy of the message to all admins
            for i in ADMINS:
                send_message(i, message_to_admin+message_body, TSW_TOKEN)
            print(message_to_admin+message_body)

    except KeyboardInterrupt:
        print("\n\nError! Please enter a valid url or close the program\n\n")
    main()


if __name__ == "__main__":
    main()