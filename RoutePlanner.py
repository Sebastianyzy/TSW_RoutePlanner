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
api_message = "https://api.keeptruckin.com/v2/messages?"
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


def send_message(sender_id, receiver_ids, message_body, TOKEN):
    url = ""
    if isinstance(receiver_ids, list):
        recivers = ""
        for i in receiver_ids:
            recivers += "{},".format(str(i))
        url = "{}sender_id={}&receiver_ids={}&body={}".format(
            api_message, str(sender_id), quote(recivers), message_body)
    else:
        url = "{}sender_id={}&receiver_ids={}&body={}".format(
            api_message, str(sender_id), str(receiver_ids), message_body)

    headers = {
        "accept": "application/json",
        "X-Api-Key": get_file_content(TOKEN),
    }
    response = requests.post(url, headers=headers)
    if response.status_code >= 300:
        print("\nMessage failed to deliver!\n{}\n{}\n".format(response, response.text, response.reason))
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
            driver.refresh()
            time.sleep(8)
            url_to_send = driver.current_url
            url_to_send = "https://www.google.com/maps/dir/Toronto+Sun+Wah+Trading,+18+Canmotor+Ave,+Etobicoke,+ON+M8Z+4E5/60+Talbot+St+N,+Essex,+ON+N8M+1A2/319+Erie+St+S,+Leamington,+ON+N8H+3C8/190+King+St+W,+Harrow,+ON+N0R+1G0/473+Sandwich+St+S,+Amherstburg,+ON+N9V+3G5/2045+Wyandotte+St+W,+Windsor,+ON+N9B+1J8/157+Erie+St+E,+Windsor,+ON+N9A+3W9/5011+Legacy+Park+Dr,+Windsor,+ON+N8W+5S6/East+Park+Centre,+6711+Tecumseh+Rd+E,+Windsor,+ON+N8T+3K7/1140+Lauzon+Rd,+Windsor,+ON+N8S+3N1/838+Smeeton+Dr,+Windsor,+ON+N8S+3X5/11925+Tecumseh+Rd+E,+Windsor,+ON+N8N+1L8/12049+Tecumseh+Rd+E,+Windsor,+ON+N8N+1M1/13300+Tecumseh+Rd+E,+Windsor,+ON+N8N+4R8/1201+Essex+County+Rd+22,+Emeryville,+ON+N0R+1C0/Toronto+Sun+Wah+Trading,+18+Canmotor+Ave,+Etobicoke,+ON+M8Z+4E5/@42.8051256,-83.556837,7z/data=!3m1!4b1!4m97!4m96!1m5!1m1!1s0x882b362de9ebe725:0xdb1aa037a40ca818!2m2!1d-79.5113742!2d43.6229466!1m5!1m1!1s0x883ad753667a73cd:0x6a0a3170648f4e4b!2m2!1d-82.8226366!2d42.1748803!1m5!1m1!1s0x883ac0544f2bf7dd:0x92fc2a6bc5d7f745!2m2!1d-82.6014442!2d42.0343942!1m5!1m1!1s0x883b2013704a242d:0x6deb4161c4c6f34f!2m2!1d-82.9224373!2d42.0359556!1m5!1m1!1s0x883b3c9143f53f05:0x7ced52ca37c69289!2m2!1d-83.106886!2d42.094309!1m5!1m1!1s0x883b2d74913c5209:0x36590791638f3d3d!2m2!1d-83.0593559!2d42.3059702!1m5!1m1!1s0x883b2cfcabbc8bfb:0xbc05be376834e2cc!2m2!1d-83.0310019!2d42.3097621!1m5!1m1!1s0x883b29639e3a07b5:0x6c6919addf2a8a0f!2m2!1d-82.9636451!2d42.2529329!1m5!1m1!1s0x883b2ae6f3ed3de3:0x7846fc0d8a32fccb!2m2!1d-82.9423413!2d42.3108897!1m5!1m1!1s0x883b2ace2bdef8c5:0x7b9484af0adb53ad!2m2!1d-82.939095!2d42.3267142!1m5!1m1!1s0x883b2acb581aea3d:0x7413cd3259cf3518!2m2!1d-82.9339657!2d42.3327876!1m5!1m1!1s0x883ad569d53f5ee3:0x95999ebedd2cab01!2m2!1d-82.8936319!2d42.3112668!1m5!1m1!1s0x883ad541fcf8bd3f:0xb54d16bce0366956!2m2!1d-82.8903898!2d42.3111988!1m5!1m1!1s0x883ad523ca256d0f:0x9db801dc83ba2775!2m2!1d-82.8706618!2d42.3125867!1m5!1m1!1s0x883ad2ec1adcafa9:0x5ab73cba82ec8a9b!2m2!1d-82.7612174!2d42.2974642!1m5!1m1!1s0x882b362de9ebe725:0xdb1aa037a40ca818!2m2!1d-79.5113742!2d43.6229466"
            driver.close()
            message_to_admin = "\nThe Following Message Was Sent To: {} (id: {})\n--------------------------------------------------------------\n".format(driver_name, driver_id)
            message_info = "Google Map Route Plan\n{} --> {} ({} stops)\n\ndate: {}\ndriver: {}\n\n".format(first_stop, last_stop, num_of_stops, order_number, driver_name)
            message_body = message_info+url_to_send
            # send message to driver
            send_message(ADMINS[0], driver_id, quote(url_to_send) , TSW_TOKEN)
            # send a copy of the message to all admins
            send_message(ADMINS[0], ADMINS, quote(message_to_admin+message_body), TSW_TOKEN)
            print(message_to_admin+message_body)

    except KeyboardInterrupt:
        print("\n\nError! Please enter a valid url or close the program\n\n")
    main()


if __name__ == "__main__":
    main()
