from flask import Flask, render_template, request, redirect, url_for, Response
import io 
import json
import numpy as np 
import os 

import matplotlib.pyplot as plt 
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from onshape_client.client import Client
from onshape_client.onshape_url import OnshapeElement

plt.rcParams['figure.figsize'] = (4, 3)
plt.rcParams['figure.autolayout'] = True 
app = Flask(__name__)

appkey = ''
secretkey = ''
DID = ''
WID = '' 
EID = ''

base = 'https://cad.onshape.com'  # change if using an Enterprise account 
# Search and check if a file named "OnshapeAPIKey.py" exists in the folder 
for _, _, files in os.walk('.'): 
    if "OnshapeAPIKey.py" in files: 
        exec(open('OnshapeAPIKey.py').read())
        appkey = access
        secretkey = secret
        break 


@app.route('/')
def index():
    return redirect(url_for("login"))


@app.route('/login')
def login():
    global appkey
    global secretkey
    global DID
    global WID
    global EID

    if appkey: 
        APPKEY = appkey 
    else: 
        APPKEY = None 
    if secretkey: 
        SECRETKEY = secretkey
    else: 
        SECRETKEY = None 
        
    DID = request.args.get('documentId')
    WID = request.args.get('workspaceId')
    EID = request.args.get('elementId')
    return render_template('login.html', APPKEY=APPKEY, SECRETKEY=SECRETKEY, DID=DID, WID=WID, EID=EID)


@app.route('/config')
def config():
    global appkey
    global secretkey
    global DID
    global WID
    global EID
    
    if not appkey or not secretkey: 
        appkey = request.args.get('appkey')
        secretkey = request.args.get('secretkey')
    if not DID or not WID or not EID: 
        DID = request.args.get('did') 
        WID = request.args.get('wid')
        EID = request.args.get('eid')
    step = float(request.args.get('step'))

    client = Client(configuration={"base_url": base, "access_key": appkey, "secret_key": secretkey})

    input_x_pos = [] 
    input_y_pos = [] 
    output_x_pos = [] 
    output_y_pos = [] 

    rotation_step = step * np.pi / 180  # in radian 
    URL = '{}/documents/{}/w/{}/e/{}'.format(str(base), str(DID), str(WID), str(EID))

    assembly_info = getAssemblyDefinition(client, URL)
    in_pos = get_position(assembly_info, 'MrKVHwm/CqMOEFTa7')
    out_pos = get_position(assembly_info, 'M7jknQrPGALQtDQ4j')
    if in_pos and out_pos: 
        input_x_pos.append(in_pos[0])
        input_y_pos.append(in_pos[1])
        output_x_pos.append(out_pos[0])
        output_y_pos.append(out_pos[1])
        for i in range(int(360 / step)): 
            # Rotate the input by rotation_step 
            rotate_input(client, assembly_info, URL, 'MrKVHwm/CqMOEFTa7', rotation_step)
            # Get the x-y position of the input and output position trackers 
            assembly_info = getAssemblyDefinition(client, URL)
            in_pos = get_position(assembly_info, 'MrKVHwm/CqMOEFTa7')
            out_pos = get_position(assembly_info, 'M7jknQrPGALQtDQ4j')
            input_x_pos.append(in_pos[0])
            input_y_pos.append(in_pos[1])
            output_x_pos.append(out_pos[0])
            output_y_pos.append(out_pos[1])
    
    # Plot the path 
    fig = Figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(input_x_pos, input_y_pos, label='Input')
    ax.plot(output_x_pos, output_y_pos, label='Output')
    ax.legend()

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# ################# Helper functions ####################################################################
def rotate_input(client, assembly, url: str, partId: str, rotation: float): 
    """
    This function rotates the input link of the mechanism 
    with a fixed rotation step in degree; changes are 
    made to the actual model 
    """
    identity_matrix = np.reshape([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], (4,4))
    occurrences = assembly['rootAssembly']['occurrences']
    occurrence = None
    for x in occurrences:
        if x['path'][0] == partId:
            occurrence = x
    if not occurrence: 
        print("Part not found!")
        return None
    
    rotMat = np.matmul(identity_matrix,clockwiseSpinZ(rotation))
    transformMat = np.matmul(identity_matrix,rotMat)

    fixed_url = '/api/assemblies/d/did/w/wid/e/eid/occurrencetransforms'
    element = OnshapeElement(url)
    base = element.base_url
    fixed_url = fixed_url.replace('did', element.did)
    fixed_url = fixed_url.replace('wid', element.wvmid)
    fixed_url = fixed_url.replace('eid', element.eid)

    method = 'POST'
    params = {}
    payload = {'isRelative': True,
               'occurrences': [occurrence],
               'transform': list(np.reshape(transformMat, -1))}
    headers = {'Accept': 'application/vnd.onshape.v1+json; charset=UTF-8;qs=0.1',
               'Content-Type': 'application/json'}

    client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)


def getAssemblyDefinition(client, url: str):
    """
    This function gets the definition of the assembly, 
    including information of all part instances and mate features 
    """
    fixed_url = '/api/assemblies/d/did/w/wid/e/eid'
    element = OnshapeElement(url)
    base = element.base_url
    fixed_url = fixed_url.replace('did', element.did)
    fixed_url = fixed_url.replace('wid', element.wvmid)
    fixed_url = fixed_url.replace('eid', element.eid)

    method = 'GET'
    params = {}
    payload = {}
    headers = {'Accept': 'application/vnd.onshape.v1+json; charset=UTF-8;qs=0.1',
                'Content-Type': 'application/json'}

    response = client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)
    parsed = json.loads(response.data)
    return parsed


def clockwiseSpinZ(theta):
    m = [[np.cos(theta), np.sin(theta), 0, 0],
        [-np.sin(theta), np.cos(theta), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]]
    return m


def get_position(assembly, partId: str): 
    """
    This function parses through all the parts within the assembly 
    and returns the x and y positions of the position trackers specified 
    with the partId. 
    """
    for occ in assembly['rootAssembly']['occurrences']: 
        if occ['path'][0] == partId: 
            return occ['transform'][3], occ['transform'][7]
    print("Part not found!") 
    return None 
