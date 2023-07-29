from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import json
import requests
import re
import m3u8
import os
    
WVD_PATH = './WVD.wvd'
    
def manifest_to_pssh(manifest_url):
    m3u8_obj = m3u8.loads(requests.get(manifest_url).content.decode())
    
    for key in m3u8_obj.keys:
        if key:
            return key.uri.split(",",1)[1]
        else:
            quit()

def do_cdm(pssh, license_url):
    pssh = PSSH(pssh)

    device = Device.load(WVD_PATH)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    challenge = cdm.get_license_challenge(session_id, pssh)

    licence = requests.post(license_url, data=challenge)
    licence.raise_for_status()

    cdm.parse_license(session_id, licence.json()['ckc'])

    fkeys = ""
    for key in cdm.get_keys(session_id):
                if key.type != 'SIGNING':
                    fkeys += key.kid.hex + ":" + key.key.hex() + "\n"
    
    print("\nKeys:")
    print(fkeys)

    cdm.close(session_id)
 
def getvinfo(url):
    response = requests.get(url).content.decode()
    
    rjson = json.loads(re.findall(r'\((.*)\)', response)[0])
    
    r = {}
    
    try:
        r['master_url'] = rjson['play']['masterurl'][0]
    except:
        r['master_url'] = None
    
    vi = rjson['vl']['vi'][0]
    
    r['title'] = vi['ti']
    
    try:
        r['license_url'] = vi['ckc']
    except:
        r['license_url'] = None
    
    ul_ui = vi['ul']['ui']
    
    r['video_url'] = ul_ui[0]['url']
    r['audio_url'] = ul_ui[1]['url']
    
    return r


getvinfo_url = input("Enter getvinfo url: ")

data = getvinfo(getvinfo_url)

title = data['title']
master_url = data['master_url']
license_url = data['license_url']
video_url = data['video_url']
audio_url = data['audio_url']

os.system('cls||clear')

print(title)

if master_url is not None:
    print('\nUrl: ' + master_url)
else:  
    print("\nVideo url: " + video_url)
    print("\nAudio url: " + audio_url)

if license_url is None:
    print('\nVideo/audio are not drm protected')

pssh = manifest_to_pssh(video_url)
do_cdm(pssh, license_url)