from flask import Flask
import time
import requests

app = Flask(__name__)

sonos_api_url = "http://192.168.7.97:5005"

sonos_owens_room = "Owen%E2%80%99s%20Room"
sonos_bedroom = "Bedroom"
sonos_livingroom = "Living%20Room"
sonos_office = "Office"

state_on = True
state_off = False

whitenoise_song_title = "Beach"

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
        json = sonos_api_call(f"[{sonos_player}] get state", f"{sonos_api_url}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == whitenoise_song_title:
            return True
        else:
            return False
    except:
        return False

def sonos_api_repeat(sonos_player, desired_state):

    if desired_state == state_on:
        sonos_repeat_value = "all"
    else:
        sonos_repeat_value = "none"
       
    attempt_number = 1
    max_number_of_attempts = 5
    repeat_value_is_correct = False

    while repeat_value_is_correct == False and attempt_number <= max_number_of_attempts:
        try:
            sonos_api_call(f"[{sonos_player}] set repeat {sonos_repeat_value}", f"{sonos_api_url}/{sonos_player}/repeat/{sonos_repeat_value}")
            json = sonos_api_call(f"[{sonos_player}] get state", f"{sonos_api_url}/{sonos_player}/state")
            if json["playMode"]["repeat"] == sonos_repeat_value:
                repeat_value_is_correct = True
            else:
                attempt_number += 1
                time.sleep(1)
        except:
            pass
    
    return repeat_value_is_correct

def sonos_api_crossfade(sonos_player, desired_state):

    if desired_state == state_on:
        sonos_crossfade_value = "on"
    else:
        sonos_crossfade_value = "off"
       
    attempt_number = 1
    max_number_of_attempts = 5
    crossfade_value_is_correct = False

    while crossfade_value_is_correct == False and attempt_number <= max_number_of_attempts:
        try:
            sonos_api_call(f"[{sonos_player}] set crossfade {sonos_crossfade_value}", f"{sonos_api_url}/{sonos_player}/crossfade/{sonos_crossfade_value}")
            json = sonos_api_call(f"[{sonos_player}] get state", f"{sonos_api_url}/{sonos_player}/state")
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

    if sonos_api_check_if_beachisplaying(sonos_owens_room):
        sonos_api_call("[bedroom] pause", f"{sonos_api_url}/{sonos_bedroom}/pause")
        sonos_api_call("[living room] pause", f"{sonos_api_url}/{sonos_livingroom}/pause")

        sonos_api_call("[bedroom]  ungroup", f"{sonos_api_url}/{sonos_bedroom}/leave")
        sonos_api_call("[living room] ungroup", f"{sonos_api_url}/{sonos_livingroom}/leave")

        sonos_api_call("[bedroom] set volume", f"{sonos_api_url}/{sonos_bedroom}/volume/40")
        sonos_api_call("[living room] set volume", f"{sonos_api_url}/{sonos_livingroom}/volume/50")
        
        sonos_api_call("[bedroom] join owen's room",f"{sonos_api_url}/{sonos_bedroom}/join/{sonos_owens_room}")
        sonos_api_call("[living room] join owen's room",f"{sonos_api_url}/{sonos_livingroom}/join/{sonos_owens_room}")

    else:
        sonos_api_call("[bedroom] pause", f"{sonos_api_url}/{sonos_bedroom}/pause")
        sonos_api_call("[living room] pause", f"{sonos_api_url}/{sonos_livingroom}/pause")
        sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")
        
        sonos_api_call("[bedroom]  ungroup", f"{sonos_api_url}/{sonos_bedroom}/leave")
        sonos_api_call("[living room] ungroup", f"{sonos_api_url}/{sonos_livingroom}/leave")
        sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
        
        sonos_api_call("[bedroom] set volume", f"{sonos_api_url}/{sonos_bedroom}/volume/40")
        sonos_api_call("[living room] set volume", f"{sonos_api_url}/{sonos_livingroom}/volume/50")
        sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/60")
        
        sonos_api_call("[living room] join bedroom",f"{sonos_api_url}/{sonos_livingroom}/join/{sonos_bedroom}")
        sonos_api_call("[owen's room] join bedroom",f"{sonos_api_url}/{sonos_owens_room}/join/{sonos_bedroom}")
        
        sonos_api_call("[bedroom/group] start Sleep playlist", f"{sonos_api_url}/{sonos_bedroom}/playlist/Sleep")

        sonos_api_repeat(sonos_bedroom, state_on)
        sonos_api_crossfade(sonos_bedroom, state_on)
    
    return '{"status":"success"}'

@app.route("/sonos/wake/all")
def sonos_wake_all():
    
    sonos_api_call("[bedroom] pause", f"{sonos_api_url}/{sonos_bedroom}/pause")
    sonos_api_call("[living room] pause", f"{sonos_api_url}/{sonos_livingroom}/pause")
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")

    sonos_api_call("[bedroom]  ungroup", f"{sonos_api_url}/{sonos_bedroom}/leave")
    sonos_api_call("[living room] ungroup", f"{sonos_api_url}/{sonos_livingroom}/leave")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
    
    sonos_api_call("[bedroom] set volume", f"{sonos_api_url}/{sonos_bedroom}/volume/20")
    sonos_api_call("[living room] set volume", f"{sonos_api_url}/{sonos_livingroom}/volume/30")
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/20")
    
    sonos_api_repeat(sonos_bedroom, state_off)
    sonos_api_crossfade(sonos_bedroom, state_off)
    
    sonos_api_repeat(sonos_livingroom, state_off)
    sonos_api_crossfade(sonos_livingroom, state_off)
    
    sonos_api_repeat(sonos_owens_room, state_off)
    sonos_api_crossfade(sonos_owens_room, state_off)
    
    return '{"status":"success"}'

@app.route("/sonos/sleep/owen")
def sonos_sleep_owen():
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/60")
    
    sonos_api_repeat(sonos_owens_room, state_on)
    sonos_api_crossfade(sonos_owens_room, state_on)
    
    sonos_api_call("[owen's room] start Sleep playlist", f"{sonos_api_url}/{sonos_owens_room}/playlist/Sleep")
    
    return '{"status":"success"}'

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/20")
    
    sonos_api_repeat(sonos_owens_room, state_off)
    sonos_api_crossfade(sonos_owens_room, state_off)
    
    return '{"status":"success"}'

@app.route("/sonos/officestop")
def sonos_office_stop():
    sonos_api_call("[office] pause", f"{sonos_api_url}/{sonos_office}/pause")
    sonos_api_call("[office] ungroup", f"{sonos_api_url}/{sonos_office}/leave")
    
    return '{"status":"success"}'