import requests
import json
import urllib
import urllib.parse


# Motive Token
TOKEN = "Token.txt"
TSW_TOKEN = "TSW_Token.txt"
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
        return

    return content

# concatenate the googlemap link with all the locations in trip list


def generate_route_plan(gm_prefix, trip):
    i = 0
    temp = gm_prefix
    while i < len(trip):
        temp += '/${'+trip[i]+'}'
        i += 1
    url = urllib.parse.quote(temp)
    return "https://{}".format(url)

# extract token from a link


def generate_api_link(url):
    splitted = ""
    try:
        splitted = url.split("token=")
    except:
        print("\nError! Unable to extract token from link: \n{}".format(url))
        return
    return api_prefix+splitted[1]


def load_trip(motive_link):
    trip = []
    order_number = "Unknown order_number"
    try:
        headers = {'X-Internal-Api-Key': get_file_content(TOKEN)}  # TOKEN
        data = requests.get(generate_api_link(motive_link), headers=headers)
        data = data.text
        # use a list to store all addresses

        parse_json = json.loads(data)
        # start
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
        trip.append(consignee)
        trip.append(shipper)
        i = 0
        while (i < len(dispatch_stops)):
            dispatch_parse = dispatch_stops[i]["dispatch_stop"]["dispatch_location"]
            customer_address = dispatch_parse["address1"]
            customer_city = dispatch_parse["city"]
            customer_province = dispatch_parse["state"]
            customer_zip = dispatch_parse["zip"]
            customer_country = dispatch_parse["country"]
            address_to_append = customer_address+", "+customer_city+", " + \
                customer_province+" "+customer_zip + ", " + customer_country
            trip.append(address_to_append)
            i += 1
        # final destination is the origin
        trip.append(consignee)
        # order_number on GoMotive is the date data
        order_number = parse_json["dispatch"]["order_number"]
        # return the trip list and the date of the dispatch
    except:
        print("\nError! Unable to load trip\n")
    return trip, order_number


def get_driver_id(url, TOKEN):
    driver_id = "Unknown id"
    try:
        headers = {'X-Internal-Api-Key': get_file_content(TOKEN)}
        data = requests.get(generate_api_link(url), headers=headers)
        data = data.text
        parse_json = json.loads(data)
        driver_id = parse_json["dispatch"]["form_entries"][0]["form_entry"]["driver_id"]
    except:
        print("\nError! Unable to get the driver's id\n")
    return str(driver_id)


def get_user_name(driver_id, TOKEN):
    driver_name = "Anonymous"
    try:
        headers = {
            "accept": "application/json",
            "X-Api-Key": get_file_content(TOKEN)
        }
        data = requests.get(api_user+driver_id, headers=headers)
        data = data.text
        parse_json = json.loads(data)
        driver_name = parse_json["user"]["first_name"] + \
            " "+parse_json["user"]["last_name"]
    except:
        print("\nError! Unable to get driver's name")
    return str(driver_name)


def get_role_list(role, per_page, page_no, TOKEN):
    role_list = []
    try:
        url = "https://api.keeptruckin.com/v1/users?role={}&per_page={}&page_no={}".format(
            role, per_page, page_no)
        headers = {
            "accept": "application/json",
            "X-Api-Key": get_file_content(TOKEN)
        }
        data = requests.get(url, headers=headers)
        data = data.text
        parse_json = json.loads(data)
        i = 0
        while i < len(parse_json["users"]):
            role_list.append(parse_json["users"][i]["user"]["id"])
            i += 1
    except:
        print("\nError! Unable to get {} list".format(role))
    return role_list


def send_message(recipient_id, message_body, TOKEN):
    headers = {
        "accept": "application/json",
        "X-Api-Key": get_file_content(TOKEN),
    }

    requests.post("{}recipient_id={}&body={}\n\n".format(
        api_message, recipient_id, message_body), headers=headers)
    # requests.post("https://api.keeptruckin.com/v1/messages?recipient_id=3744311&body="+link,headers=headers)
    return


def main():
    try:
        # motive_link = input(
        #     "Enter the GoMotive dispatch url or close the Program : ")
        motive_link = testlk
    except KeyboardInterrupt:
        main()
    try:
        trip, order_number = load_trip(motive_link)
        url = generate_route_plan(googlemap_prefix, trip)
        driver_id = get_driver_id(motive_link, TOKEN)
        driver_name = get_user_name(driver_id, TSW_TOKEN)

        message_to_admin = "\nThe Following Message Was Sent To: {} (id: {})\n-------------------------------------------------------------\n".format(
            driver_name, driver_id)
        message_body = "Google Map Route URL For: {}\n\n{}".format(
            order_number, url)

        # send message to driver
        send_message(driver_id, message_body, TSW_TOKEN)
        # get all the admin_id
        ADMINS = get_role_list("admin", 25, 1, TSW_TOKEN)
        # send a copy of the message to all admins
        for admin in ADMINS:
            send_message(admin, message_to_admin+message_body, TSW_TOKEN)

        print(message_to_admin+message_body)

    except:
        print("\nError! Please enter a valid url or close the program\n")
    main()


if __name__ == "__main__":
    main()
