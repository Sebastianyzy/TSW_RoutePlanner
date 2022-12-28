import requests
import json


TOKEN = "TFpmKLsjnGbQYYwbFX5vggLgv0Rdft"
api_prefix = "https://api.keeptruckin.com/api/i1/dispatch_share?token="
googlemap_prefix = "https://www.google.com/maps/dir"


def get_token(TOKEN):
    file = open(TOKEN, "r")
    token = file.read()
    token = str(token)
    file.close()
    return str(token)


def generate_route_plan(gm_prefix, trip):
    i = 0
    url = gm_prefix
    while i < len(trip):
        url += "/${"+trip[i]+"}"
        i += 1
    return str(url)


def generate_api_link(url):
    splitted = url.split("token=")
    return api_prefix+splitted[1]


def load_trip(motive_link):   
    headers = {'X-Internal-Api-Key': TOKEN}#get_token(TOKEN)
    data = requests.get(generate_api_link(motive_link), headers=headers)
    data = data.text
    trip = []
    parse_json = json.loads(data)
    consignee_dispatch_location = parse_json["dispatch"]["consignee_dispatch_location"]
    shipper_dispatch_location = parse_json["dispatch"]["shipper_dispatch_location"]
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
        trip.append(dispatch_stops[i]["dispatch_stop"]["dispatch_location"]["address1"]+", "+dispatch_stops[i]["dispatch_stop"]["dispatch_location"]["city"]+", " + dispatch_stops[i]["dispatch_stop"]
                    ["dispatch_location"]["state"]+" "+dispatch_stops[i]["dispatch_stop"]["dispatch_location"]["zip"] + ", " + dispatch_stops[i]["dispatch_stop"]["dispatch_location"]["country"])
        i += 1
    trip.append(consignee)
    return trip


def main():
    motive_link = input("Enter the GoMotive dispatch url or close the Program : ")
    try:       
        trip = load_trip(motive_link)
        print("\nCopy the Following Link and Send to Drivers:\n"+"\n"+generate_route_plan(googlemap_prefix, trip)+"\n")
    except:
        print("\nError! Please enter a valid url or close the program\n")
    main()
    
if __name__ == "__main__":
    main()
