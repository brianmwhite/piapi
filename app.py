from flask import Flask
import time
import requests
import os

app = Flask(__name__)

SONOS_API_IP = os.environ["SONOS_API_IP"]
SONOS_API_URL = f"http://{SONOS_API_IP}"

SONOS_OWENS_ROOM = "Owen%E2%80%99s%20Room"
SONOS_BEDROOM = "Bedroom"
SONOS_LIVINGROOM = "Living%20Room"
SONOS_OFFICE = "Office"

STATE_ON = True
STATE_OFF = False

REPEAT_ALL_VALUE = "all"
REPEAT_OFF_VALUE = "none"

CROSSFADE_ON_VALUE = "on"
CROSSFADE_OFF_VALUE = "off"

# Instructions on creating a user on your hue hub
# create a 'user' : curl -X POST -d '{"devicetype":"my app"}' http://$ADDR/api
# get status of all lights : curl http://$ADDR/api/$HUE_USER/lights/
# info from https://github.com/tigoe/hue-control

HUE_USER = os.environ["HUE_USER"]
HUE_HUB_IP = os.environ["HUE_HUB_IP"]
HUEGO_ID = 2
HUE_SET_STATE_URL = f"http://{HUE_HUB_IP}/api/{HUE_USER}/lights/{HUEGO_ID}/state"
HUE_GET_STATE_URL = f"http://{HUE_HUB_IP}/api/{HUE_USER}/lights/{HUEGO_ID}"
HUE_WHITE_VALUE = '{"on": true, "bri": 254, "hue": 41402, "sat": 74, "effect": "none", "xy": [0.3155, 0.3313 ], "ct": 158}'
HUE_RED_VALUE = '{"on": true, "bri": 254, "hue": 65202, "sat": 254, "effect": "none", "xy": [0.6817, 0.3036 ], "ct": 153 }'
HUE_OFF_VALUE = '{"on":false}'

def huego_setstate(action, value):
    r = requests.put(HUE_SET_STATE_URL, data=value)
    json_response = r.text
    print(f"Hue set state {action}={json_response}")
    print(json_response)
    return json_response

def huego_check_if_alert_is_on():
    r = requests.get(HUE_GET_STATE_URL)
    json_response = r.json()
    if json_response["state"]["on"] == True and json_response["state"]["hue"] == 65202 and json_response["state"]["sat"] == 254:
        return True
    else:
        return False

def huego_check_if_light_is_off():
    r = requests.get(HUE_GET_STATE_URL)
    json_response = r.json()
    if json_response["state"]["on"] == False:
        return True
    else:
        return False

def huego_video_alert_on():
    attempt_number = 1
    max_number_of_attempts = 5
    value_is_correct = False
    json_response = "{}"

    while value_is_correct == False and attempt_number <= max_number_of_attempts:
        json_response = huego_setstate("video on",HUE_RED_VALUE)
        if huego_check_if_alert_is_on():
            value_is_correct = True
        else:
            attempt_number += 1
            time.sleep(1)
    return json_response

def huego_video_alert_off():   
    attempt_number = 1
    max_number_of_attempts = 5
    value_is_correct = False
    json_response = "{}"

    while value_is_correct == False and attempt_number <= max_number_of_attempts:
        json_response = huego_setstate("video off",HUE_OFF_VALUE)
        if huego_check_if_light_is_off():
            value_is_correct = True
        else:
            attempt_number += 1
            time.sleep(1)
    return json_response

@app.route("/videoalert/on")
def huego_video_on_action():
    return huego_video_alert_on()

@app.route("/videoalert/off")
def huego_video_off_action():
    return huego_video_alert_off()

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
        if json["playbackState"] == "PLAYING" and json["playMode"]["repeat"] == REPEAT_ALL_VALUE and json["playMode"]["crossfade"] == CROSSFADE_ON_VALUE:
            return True
        else:
            return False
    except:
        return False

def sonos_api_repeat(sonos_player, desired_state):

    if desired_state == STATE_ON:
        sonos_repeat_value = REPEAT_ALL_VALUE
    else:
        sonos_repeat_value = REPEAT_OFF_VALUE
       
    attempt_number = 1
    max_number_of_attempts = 5
    repeat_value_is_correct = False

    while repeat_value_is_correct == False and attempt_number <= max_number_of_attempts:
        try:
            sonos_api_call(f"[{sonos_player}] set repeat {sonos_repeat_value}", f"{SONOS_API_URL}/{sonos_player}/repeat/{sonos_repeat_value}")
            json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
            if json["playMode"]["repeat"] == sonos_repeat_value:
                repeat_value_is_correct = True
            else:
                attempt_number += 1
                time.sleep(1)
        except:
            pass
    
    return repeat_value_is_correct

def sonos_api_crossfade(sonos_player, desired_state):

    if desired_state == STATE_ON:
        sonos_crossfade_value = CROSSFADE_ON_VALUE
    else:
        sonos_crossfade_value = CROSSFADE_OFF_VALUE
       
    attempt_number = 1
    max_number_of_attempts = 5
    crossfade_value_is_correct = False

    while crossfade_value_is_correct == False and attempt_number <= max_number_of_attempts:
        try:
            sonos_api_call(f"[{sonos_player}] set crossfade {sonos_crossfade_value}", f"{SONOS_API_URL}/{sonos_player}/crossfade/{sonos_crossfade_value}")
            json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
            if json["playMode"]["crossfade"] == desired_state:
                crossfade_value_is_correct = True
            else:
                attempt_number += 1
                time.sleep(1)
        except:
            pass
    
    return crossfade_value_is_correct

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

        sonos_api_repeat(SONOS_BEDROOM, STATE_ON)
        sonos_api_crossfade(SONOS_BEDROOM, STATE_ON)
    
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
    
    sonos_api_repeat(SONOS_BEDROOM, STATE_OFF)
    sonos_api_crossfade(SONOS_BEDROOM, STATE_OFF)
    
    sonos_api_repeat(SONOS_LIVINGROOM, STATE_OFF)
    sonos_api_crossfade(SONOS_LIVINGROOM, STATE_OFF)
    
    sonos_api_repeat(SONOS_OWENS_ROOM, STATE_OFF)
    sonos_api_crossfade(SONOS_OWENS_ROOM, STATE_OFF)
    
    return '{"status":"success"}'

@app.route("/sonos/sleep/owen")
def sonos_sleep_owen():
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/60")
    
    sonos_api_repeat(SONOS_OWENS_ROOM, STATE_ON)
    sonos_api_crossfade(SONOS_OWENS_ROOM, STATE_ON)
    
    sonos_api_call("[owen's room] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/playlist/Sleep")
    
    return '{"status":"success"}'

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/20")
    
    sonos_api_repeat(SONOS_OWENS_ROOM, STATE_OFF)
    sonos_api_crossfade(SONOS_OWENS_ROOM, STATE_OFF)
    
    return '{"status":"success"}'

@app.route("/sonos/officestop")
def sonos_office_stop():
    sonos_api_call("[office] mute", f"{SONOS_API_URL}/{SONOS_OFFICE}/mute")
    sonos_api_call("[office] ungroup", f"{SONOS_API_URL}/{SONOS_OFFICE}/leave")
    sonos_api_call("[office] pause", f"{SONOS_API_URL}/{SONOS_OFFICE}/pause")

    return '{"status":"success"}'