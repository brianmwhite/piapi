from flask import Flask
import time
import requests
import os
import jmespath
import sonos_control

app = Flask(__name__)

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

@app.route("/sonos/sleep/all")
def api_sonos_sleep_all():
    return sonos_control.sonos_sleep_all()

@app.route("/sonos/wake/all")
def api_sonos_wake_all():
    return sonos_control.sonos_wake_all()

@app.route("/sonos/get_white_noise_state/owen")
def api_sonos_get_white_noise_state_owen():
    return sonos_control.sonos_get_white_noise_state_owen()

@app.route("/sonos/sleep/owen")
def api_sonos_sleep_owen():
    return sonos_control.sonos_sleep_owen()

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    return sonos_control.sonos_wake_owen()

@app.route("/sonos/get_white_noise_state/bedroom")
def api_sonos_get_white_noise_state_bedroom():
    return sonos_control.sonos_get_white_noise_state_bedroom()

@app.route("/sonos/sleep/bedroom")
def api_sonos_sleep_bedroom():
    return sonos_control.sonos_sleep_bedroom()

@app.route("/sonos/wake/bedroom")
def api_sonos_wake_bedroom():
    return sonos_control.sonos_wake_bedroom()

@app.route("/sonos/officestop")
def api_sonos_office_stop():
    return sonos_control.sonos_office_stop()

@app.route("/sonos/officeunmute")
def api_sonos_office_unmute():
    return sonos_control.sonos_office_unmute()

@app.route("/sonos/ungroup/all")
def api_sonos_ungroup_all():
    return sonos_control.sonos_ungroup_all()