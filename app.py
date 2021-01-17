from flask import Flask
import time
import requests
import os
import jmespath

app = Flask(__name__)

# jishi / node-sonos-http-api
# https://github.com/jishi/node-sonos-http-api

SONOS_API_IP = os.environ["SONOS_API_IP"]
SONOS_API_URL = f"http://{SONOS_API_IP}"

SONOS_OWENS_ROOM = "Owen%E2%80%99s%20Room"
SONOS_BEDROOM = "Bedroom"
SONOS_LIVINGROOM = "Living%20Room"
SONOS_OFFICE = "Office"
WHITE_NOISE_TRACK_TITLE = "Beach with Cross Fade"
STATE_ON = True
STATE_OFF = False

# Instructions on creating a user on your hue hub
# create a 'user' : curl -X POST -d '{"devicetype":"my app"}' http://$ADDR/api
# get status of all lights : curl http://$ADDR/api/$HUE_USER/lights/
# info from https://github.com/tigoe/hue-control

HUE_USER = os.environ["HUE_USER"]
HUE_HUB_IP = os.environ["HUE_HUB_IP"]
HUEGO_ID = 2
HUE_SET_STATE_URL = f"http://{HUE_HUB_IP}/api/{HUE_USER}/lights/{HUEGO_ID}/state"
HUE_GET_STATE_URL = f"http://{HUE_HUB_IP}/api/{HUE_USER}/lights/{HUEGO_ID}"

HUE_RED_VALUE =     '{"on": true, "bri": 254, "hue": 65202, "sat": 254, "effect": "none", "xy": [0.6817, 0.3036], "ct": 153 }'
HUE_ORANGE_VALUE =  '{"on": true, "bri": 254, "hue": 3224, "sat": 254, "effect": "none", "xy": [0.6179, 0.3679], "ct": 153 }'
HUE_YELLOW_VALUE =  '{"on": true, "bri": 254, "hue": 8414, "sat": 254, "effect": "none", "xy": [0.5201, 0.4370], "ct": 484 }'
HUE_GREEN_VALUE =   '{"on": true, "bri": 254, "hue": 21670, "sat": 254, "effect": "none", "xy": [0.2500,0.6399], "ct": 153 }'
HUE_BLUE_VALUE =    '{"on": true, "bri": 254, "hue": 42202, "sat": 254, "effect": "none", "xy": [0.1570,0.1963], "ct": 153 }'
HUE_PURPLE_VALUE =  '{"on": true, "bri": 254, "hue": 49429, "sat": 220, "effect": "none", "xy": [0.2736,0.1323], "ct": 153 }'
HUE_PINK_VALUE =    '{"on": true, "bri": 254, "hue": 58433, "sat": 248, "effect": "none", "xy": [0.4816,0.2118], "ct": 406 }'
HUE_WHITE_VALUE =   '{"on": true, "bri": 254, "hue": 41402, "sat": 74, "effect": "none", "xy": [0.3155, 0.3313 ], "ct": 158}'
HUE_OFF_VALUE =     '{"on":false}'

def lookup_hue_colorname_to_value(color_name):
    hue_color_value = HUE_OFF_VALUE
    if color_name == "RED":
        hue_color_value = HUE_RED_VALUE
    elif color_name == "ORANGE":
        hue_color_value = HUE_ORANGE_VALUE
    elif color_name == "YELLOW":
        hue_color_value = HUE_YELLOW_VALUE
    elif color_name == "GREEN":
        hue_color_value = HUE_GREEN_VALUE
    elif color_name == "BLUE":
        hue_color_value = HUE_BLUE_VALUE
    elif color_name == "PURPLE":
        hue_color_value = HUE_PURPLE_VALUE
    elif color_name == "PINK":
        hue_color_value = HUE_PINK_VALUE
    elif color_name == "WHITE":
        hue_color_value = HUE_WHITE_VALUE
    elif color_name == "OFF":
        hue_color_value = HUE_OFF_VALUE
    return hue_color_value

def huego_setstate(action, value):
    r = requests.put(HUE_SET_STATE_URL, data=value)
    json_response = r.text
    print(f"Hue set state {action}={json_response}")
    print(json_response)
    return json_response

def huego_check_if_light_is_correct_state(desired_state):
    r = requests.get(HUE_GET_STATE_URL)
    json_response = r.json()
    if json_response["state"]["on"] == desired_state:
        return True
    else:
        return False

def huego_check_if_light_is_on():
    return huego_check_if_light_is_correct_state(True)

def huego_check_if_light_is_off():
    return huego_check_if_light_is_correct_state(False)

def huego_light_on_to_color(color_name):
    attempt_number = 1
    max_number_of_attempts = 5
    value_is_correct = False
    json_response = "{}"
    hue_value = lookup_hue_colorname_to_value(color_name)

    while value_is_correct == False and attempt_number <= max_number_of_attempts:
        json_response = huego_setstate(color_name, hue_value)
        
        if color_name == "OFF":
            if huego_check_if_light_is_off():
                value_is_correct = True 
        else:
            if huego_check_if_light_is_on():
                value_is_correct = True 

        if not value_is_correct:
            attempt_number += 1
            time.sleep(1)

    return json_response

@app.route("/videoalert/on")
def huego_video_on_action():
    return huego_light_on_to_color("RED")

@app.route("/videoalert/off")
def huego_video_off_action():
    return huego_light_on_to_color("OFF")

@app.route("/alert/setcolor/<color>")
def huego_alert_color_action(color):
    color_name = color.upper()
    return huego_light_on_to_color(color_name)

def sonos_api_call(action, url):
    json = "{}"
    try:
        r = requests.get(url)
        print(f"{action}={r.json()}")
        json = r.json()
    except:
        pass
    return json

def sonos_api_check_if_beachisplaying(sonos_player):
    try:
        json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE:
            return True
        else:
            return False
    except:
        return False

@app.route("/sonos/sleep/all")
def sonos_sleep_all():

    if sonos_api_check_if_beachisplaying(SONOS_OWENS_ROOM):
        sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
        sonos_api_call("[living room] pause", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/pause")

        sonos_api_call("[bedroom]  ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
        sonos_api_call("[living room] ungroup", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/leave")

        sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/40")
        sonos_api_call("[living room] set volume", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/volume/50")
        
        sonos_api_call("[bedroom] join owen's room",f"{SONOS_API_URL}/{SONOS_BEDROOM}/join/{SONOS_OWENS_ROOM}")
        sonos_api_call("[living room] join owen's room",f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/join/{SONOS_OWENS_ROOM}")

    else:
        sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
        sonos_api_call("[living room] pause", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/pause")
        sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
        
        sonos_api_call("[bedroom]  ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
        sonos_api_call("[living room] ungroup", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/leave")
        sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
        
        sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/40")
        sonos_api_call("[living room] set volume", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/volume/50")
        sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/60")
        
        sonos_api_call("[living room] join bedroom",f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/join/{SONOS_BEDROOM}")
        sonos_api_call("[owen's room] join bedroom",f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/join/{SONOS_BEDROOM}")
        
        sonos_api_call("[bedroom/group] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_BEDROOM}/playlist/Sleep")

    return '{"status":"success"}'

@app.route("/sonos/wake/all")
def sonos_wake_all():
    
    sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
    sonos_api_call("[living room] pause", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/pause")
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")

    sonos_api_call("[bedroom]  ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
    sonos_api_call("[living room] ungroup", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/leave")
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    
    sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/20")
    sonos_api_call("[living room] set volume", f"{SONOS_API_URL}/{SONOS_LIVINGROOM}/volume/30")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/20")
    
    return '{"status":"success"}'

@app.route("/sonos/get_white_noise_state/Owen")
def sonos_get_white_noise_state_owen():
    if sonos_api_check_if_beachisplaying(SONOS_OWENS_ROOM):
        return '{"white_noise_on":true}'
    else:
        return '{"white_noise_on":false}'

@app.route("/sonos/sleep/owen")
def sonos_sleep_owen():
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/60")
    
    sonos_api_call("[owen's room] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/playlist/Sleep")
    
    return '{"status":"success"}'

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/20")
    
    return '{"status":"success"}'

@app.route("/sonos/get_white_noise_state/bedroom")
def sonos_get_white_noise_state_bedroom():
    if sonos_api_check_if_beachisplaying(SONOS_BEDROOM):
        return '{"white_noise_on":true}'
    else:
        return '{"white_noise_on":false}'

@app.route("/sonos/sleep/bedroom")
def sonos_sleep_bedroom():

    if sonos_api_check_if_beachisplaying(SONOS_OWENS_ROOM):
        sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
        sonos_api_call("[bedroom] ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
        sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/40")       
        sonos_api_call("[bedroom] join owen's room",f"{SONOS_API_URL}/{SONOS_BEDROOM}/join/{SONOS_OWENS_ROOM}")
    else:
        sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")       
        sonos_api_call("[bedroom] ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
        sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/40")
        sonos_api_call("[bedroom/group] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_BEDROOM}/playlist/Sleep")

    return '{"status":"success"}'

@app.route("/sonos/wake/bedroom")
def sonos_wake_bedroom():
    sonos_api_call("[bedroom] ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
    sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
    sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/20")
    
    return '{"status":"success"}'


@app.route("/sonos/officestop")
def sonos_office_stop():
    sonos_api_call("[office] mute", f"{SONOS_API_URL}/{SONOS_OFFICE}/mute")
    sonos_api_call("[office] ungroup", f"{SONOS_API_URL}/{SONOS_OFFICE}/leave")
    return '{"status":"success"}'

@app.route("/sonos/officeunmute")
def sonos_office_unmute():
    sonos_api_call("[office] unmute", f"{SONOS_API_URL}/{SONOS_OFFICE}/unmute")
    return '{"status":"success"}'


@app.route("/sonos/ungroup/all")
def sonos_ungroup_all():
    zone_json_results = sonos_api_call("return zones status", f"{SONOS_API_URL}/zones")
    search_expression = jmespath.compile("[].members[].roomName")
    sonos_players = search_expression.search(zone_json_results)
    for individual_player in sonos_players:
        sonos_api_call(f"ungroup {individual_player}", f"{SONOS_API_URL}/{individual_player}/leave")
        pass
    return '{"status":"success"}'