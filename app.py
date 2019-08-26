from flask import Flask, render_template, redirect, url_for, \
                    request, send_from_directory, make_response, abort, send_file
import json
import random
import os
from winreg import *
import subprocess
import argparse
import sys
import win32serviceutil
import threading
import time
import io
import shutil
import mmap
import datetime

app = Flask(__name__)

try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]


this_file = os.path.abspath(this_file)
CURRENT_DIR = os.path.dirname(this_file)
PATH_NETDRIVE_ITEMS = os.path.join(CURRENT_DIR, "json\\netdriveItems.json")
PATH_CLOUDSYNC_ITEMS = os.path.join(CURRENT_DIR, "json\\cloudsyncItems.json")
PATH_PRODUCTS = os.path.join(CURRENT_DIR, "json\\products.json")

NAME="Me-PC"
OS="windows"

#build to executable
if getattr(sys, 'frozen', False):
    CURRENT_DIR = os.path.dirname(sys.executable)
    PATH_NETDRIVE_ITEMS = os.path.join(CURRENT_DIR, "json\\netdriveItems.json")
    PATH_CLOUDSYNC_ITEMS = os.path.join(CURRENT_DIR, "json\\cloudsyncItems.json")
    PATH_PRODUCTS = os.path.join(CURRENT_DIR, "json\\products.json")
    if not os.path.exists(PATH_NETDRIVE_ITEMS) and not os.path.exists(PATH_CLOUDSYNC_ITEMS) and not os.path.exists(PATH_PRODUCTS):
        shutil.copytree(os.path.join(sys._MEIPASS, 'json'), os.path.join(CURRENT_DIR, 'json'))


@app.route("/")
def index():
    return redirect("/accounts/login/?next=/", code = 302)

@app.route('/<path:path>')
def proxy(path):
    #return "\n", 101
    abort(404)

@app.route("/accounts/login/", methods=['GET',])
def login():
    return 'OK'
    
@app.route("/api/v1/check_auth_token/")
def auth_token():    
    payload = '{"code": 0, "message": "You are good to go."}'
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/api/v1/rest-auth/login/', methods=['POST'])
def auth_login():
    payload = '{"code": 0, "token": "9d1253d4acb57cb90d58b12b342967f7b2c0a2bf", "url": null}'
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route("/api/v1/me/products/")
def products():
    if request.args.get('name'):
        NAME = request.args.get('name')

    if request.args.get('os'):
        OS = request.args.get('os')

    resp = make_response(send_file(PATH_PRODUCTS))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Set-Cookie'] = 'sessionid=nrbw43idxks9hfkqpsp0nwlpzbdlqi7p; expires=Wed, 06-Jun-2518 19:31:03 GMT; HttpOnly; Max-Age=1209600; Path=/'
    resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
    return resp
    
@app.route("/api/v1/me/products/CloudSync/limits/")
def limits():    
    payload = '{"speed_limit": -1, "file_limit": {"num_per_sync": 100, "max_size": -1}}'
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route("/api/v1/NetDrive3/items/", methods=["POST"])
def add_netdrive_item():    
    return add_item(PATH_NETDRIVE_ITEMS)

@app.route("/api/v1/CloudSync/items/", methods=["POST"])
def add_cloudsync_item():    
    return add_item(PATH_CLOUDSYNC_ITEMS)
    
@app.route("/api/v1/NetDrive3/items/", methods=["GET"])
def get_netdrive_item():    
    return get_item(PATH_NETDRIVE_ITEMS)
    
@app.route("/api/v1/CloudSync/items/", methods=["GET"])
def get_cloudsync_item():    
    return get_item(PATH_CLOUDSYNC_ITEMS)
    
@app.route("/api/v1/NetDrive3/items/<int:item_id>/", methods=['PATCH', 'DELETE'])
def netdrive_items(item_id):
    return items(PATH_NETDRIVE_ITEMS, item_id)

@app.route("/api/v1/CloudSync/items/<int:item_id>/", methods=['PATCH', 'DELETE'])
def cloudsync_items(item_id):
    return items(PATH_CLOUDSYNC_ITEMS, item_id)    
    
@app.route("/api/v1/CloudSync/items/<int:item_id>/update_status/", methods=['POST'])
def cloudsync_update_status(item_id):
    item_id = int(item_id)
    dataChangeStatus = request.get_json()
    with open(PATH_CLOUDSYNC_ITEMS, 'r+') as f:
        database = json.load(f)
        for i in range(len(database['results'])):
            if database['results'][i]['id'] == item_id:
                if not 'item_status' in database['results'][i]:
                    id = (item_id + random.randint(0, 99))-100
                    guid = dataChangeStatus['device_guid']
                    dt = datetime.datetime.now().isoformat()
                    database['results'][i]['item_status'] = json.loads('{"device" : {  "id": ' + str(id) + ', "guid": "' + guid + '", "name": "' + NAME + '", "os": "' + OS + '", "is_active": true, "date_created": "' + dt + '" }}')
                database['results'][i]['item_status']['status'] = '"' + json.dumps(dataChangeStatus['status']) + '"'    
                break
        f.seek(0)
        f.truncate()
        json.dump(database, f)

        resp = make_response(json.dumps(database))
        resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
        resp.headers['Content-Type'] = 'application/json'
        return resp
    
@app.route('/api/v1/sso_guard/')
def sso_guard():
    payload = '{"guard":"MTUyNzUyODA3LTI3Ljc0LjI1NS4yNDE=","encoding":"sha3-256","format":"token-guard"}'
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Set-Cookie'] = 'sessionid=nrbw43idxks9hfkqpsp0nwlpzbdlqi7p; expires=Wed, 06-Jun-2518 19:31:03 GMT; HttpOnly; Max-Age=1209600; Path=/'
    return resp

def add_item(items_file_path):
    dataNew = request.get_json()
    dataNew['id'] = random.randint(1, 999999)
    with open(items_file_path, 'r+') as f:
        database = json.load(f)
        database['count'] += 1
        database['results'].append(dataNew)
        f.seek(0)
        f.truncate()
        json.dump(database, f)
    resp = make_response(json.dumps(dataNew))
    resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
    resp.headers['Content-Type'] = 'application/json'
    return resp

def get_item(items_file_path):
    if not os.path.exists(items_file_path): 
        with open(items_file_path, 'w') as f:
            f.write('{"count": 0, "previous": null, "results": [], "next": null}')
    resp = make_response(send_file(items_file_path))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Set-Cookie'] = 'sessionid=nrbw43idxks9hfkqpsp0nwlpzbdlqi7p; expires=Wed, 06-Jun-2518 19:31:03 GMT; HttpOnly; Max-Age=1209600; Path=/'
    resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
    return resp

def items(items_file_path, item_id):
    item_id = int(item_id)
    if request.method == "PATCH":
        dataUpdate = request.get_json()
        dataUpdate['id'] = item_id
        with open(items_file_path, 'r+') as f:
            database = json.load(f)
            for i in range(len(database['results'])):
                if database['results'][i]['id'] == item_id:
                    database['results'][i] = dataUpdate
                    break
            f.seek(0)
            f.truncate()
            json.dump(database, f)

        resp = make_response(json.dumps(dataUpdate))
        resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
        resp.headers['Content-Type'] = 'application/json'
        return resp

    if request.method == "DELETE":
        with open(items_file_path, 'r+') as f:
            database = json.load(f)
            for i in range(len(database['results'])):
                if database['results'][i]['id'] == item_id:
                    del database['results'][i]
                    database['count'] -= 1
                    break
            f.seek(0)
            f.truncate()
            json.dump(database, f)
            
        resp = make_response()
        resp.headers['X-Bdrive-Session-Key'] = 'd90ab0a3b35a4d59bba2f0cfed1de192'
        resp.headers['Set-Cookie'] = 'sessionid=nrbw43idxks9hfkqpsp0nwlpzbdlqi7p; expires=Wed, 06-Jun-2518 19:31:03 GMT; HttpOnly; Max-Age=1209600; Path=/'
        return resp, 204

def patchNetDrive(DirNetDrive):
    try:
        os.system('taskkill /f /im ndagent.exe')
        os.system('taskkill /f /im nd3svc.exe')
        os.system('taskkill /f /im NetDrive.exe')
        os.system('taskkill /f /im ndmnt.exe')

        NetDrivePath = os.path.join(DirNetDrive, 'NetDrive.exe')
        ndagentPath = os.path.join(DirNetDrive, 'ndagent.exe')
        shutil.copy2(NetDrivePath, os.path.join(DirNetDrive, 'NetDrive.exe.bak'))
        shutil.copy2(ndagentPath, os.path.join(DirNetDrive, 'ndagent.exe.bak'))

        with open(NetDrivePath, 'rb+') as f:
            f.seek(FindOffsetBypass(NetDrivePath))
            f.write(b'://127.0.0.1:52221')

        with open(ndagentPath, 'rb+') as f:
            f.seek(FindOffsetBypass(ndagentPath))
            f.write(b'://127.0.0.1:52221')

        pathFileHosts = os.path.join(os.environ['windir'], r'System32\drivers\etc\hosts')
        if not os.path.exists(pathFileHosts):
            with open(pathFileHosts, "a+") as f:
                f.write('127.0.0.1 localhost\r\n')

        with open(pathFileHosts, "a+") as f:
            f.write('\r\n127.0.0.1 push.bdrive.com\r\n')
        os.system('gpupdate /force')
        

    except Exception as e:
        print("Patch failed - %s" % e)
        return

    print("Patch OK")
    try:
        win32serviceutil.StartService('NetDrive3_Service_x64_NetDrive3')
    except:
        win32serviceutil.StartService('NetDrive3_Service_NetDrive3')
    win32serviceutil.StartService('NetDrive3 Agent')
    subprocess.Popen([os.path.join(DirNetDrive, 'NetDrive.exe'),], cwd = DirNetDrive)

def patchCloudSync(DirCloudSync):
    try:
        os.system('taskkill /f /im cloudsync.exe')

        CloudSyncPath = os.path.join(DirCloudSync, 'cloudsync.exe')
        shutil.copy2(CloudSyncPath, os.path.join(DirCloudSync, 'cloudsync.exe.bak'))
        with open(CloudSyncPath, 'rb+') as f:
            f.seek(FindOffsetBypass(CloudSyncPath))
            f.write(b'://127.0.0.1:52221')
        
        pathFileHosts = os.path.join(os.environ['windir'], r'System32\drivers\etc\hosts')
        if not os.path.exists(pathFileHosts):
            with open(pathFileHosts, "a+") as f:
                f.write('127.0.0.1 localhost\r\n')

        with open(pathFileHosts, "a+") as f:
            f.write('\r\n127.0.0.1 push.bdrive.com\r\n')
        os.system('gpupdate /force')
        

    except Exception as e:
        print("Patch failed - %s" % e)
        return

    print("Patch OK")
    subprocess.Popen([os.path.join(DirCloudSync, 'cloudsync.exe'),], cwd = DirCloudSync)

def runServer():
    os.system('taskkill /f /im ndagent.exe')
    os.system('taskkill /f /im nd3svc.exe')
    os.system('taskkill /f /im NetDrive.exe')
    os.system('taskkill /f /im ndmnt.exe')
    os.system('taskkill /f /im cloudsync.exe')
    app.run(threaded = True, debug = False, port = 52221, host = '127.0.0.1')#, ssl_context=(PATH_CERT, PATH_KEY))

def RunAtStartup():
    try:
        key = OpenKey(HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, KEY_WRITE)
        SetValueEx(key, 'AutoServerBdrive', 0, REG_SZ, sys.executable)
        CloseKey(key)
        return True
    except WindowsError:
        return False

def RemoveRunAtStartup():
    try:
        key = OpenKey(HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, KEY_WRITE)
        DeleteValue(key, 'AutoServerBdrive')
        CloseKey(key)
        return True
    except WindowsError:
        return False
        
def FindOffsetBypass(FileName):
    with open(FileName, 'rb+') as f:
        mm = mmap.mmap(f.fileno(), 0)
        return int(mm.find(b'api.bdrive.com')) - 4

def main():
    description = """\
Please enter -n "<NetDrive3 installation path>" or --netdrive "<NetDrive3 installation path>" to patch NetDrive3
Please enter -c "<CloudSync installation path>" or --cloudsync "<CloudSync installation path>" to patch CloudSync

If no arguments, program will run the fake server\
    """
    parser = argparse.ArgumentParser(description = description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', '--netdrive', metavar = '"<NETDRIVE_INSTALLATION_FOLDER_PATH>"', type=str, help = 'Patch NetDrive3 in specified intallation directory')
    parser.add_argument('-c', '--cloudsync', metavar = '"<CLOUDSYNC_INSTALLATION_FOLDER_PATH>"', type=str, help = 'Patch CloudSync in specified intallation directory')
    parser.add_argument('-s', '--startup', action = 'store_true', help = 'Run at startup')
    parser.add_argument('-r', '--remove', action = 'store_true', help = 'Remove run at startup')
    args = parser.parse_args()

    if args.netdrive:
        patchNetDrive(args.netdrive)

    if args.cloudsync:
        patchCloudSync(args.cloudsync)
        
    if args.startup:
        if RunAtStartup():
            print("StartUp OK")
            return
        print("StartUp Failed")
        return

    if args.remove:
        if RemoveRunAtStartup():
            print("Remove OK")
            return
        print("Remove Failed")
        return

    print("Please enter --help for infomation.")
    runServer()

if __name__ == '__main__':
    main()
