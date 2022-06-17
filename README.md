# Four Bar Mechanism Design Project
This is a sample project that aims to demonstrate various possible Onshape integrations with the REST API. Speicifically, this project demonstrates two alternatives that API calls can be made: (1) simple coding in a Jupyter notebook, and (2) integration to the Onshape user interface with a Python Flask application.

Correspondingly, more detailed guides to these two integration methods can be found in [this repository](https://github.com/PTC-Education/Onshape-Integration-Guides). To really get started and learn about these methods, it is highly recommended to first go through the integration guides for the basics and then return to this project to see its capability. 

In this project, we first build an Onshape model of a simple four-bar mechanism. The four linkages are named ground, input, output, and floating, respectively. As a common introduction to kinematics analysis in mechanical engineering, varying the lengths of the four linkages results in different motions for the output linkage, while constant rotational motion is applied to the input linkage. Through making REST API calls to the Onshape document, we can simulate the motion of both the input and output linkages to generate a path plot. 

![snapshot](/assets/CAD%20Model.png)

While you can experiment with this project through (1) the Jupyter notebook version with `Four_Bar.ipynb` and (2) the Flask version, this guide will focus on steps that you need to take to launch the Flask application in your Onshape user interface. 

To integrate and use the Flask app in this project, please follow the following steps: 

1. Make a copy to [this Onshape document](https://cad.onshape.com/documents/178816b0fa7fb384c9ef431c/w/e3249365341e3ffa779dd405/e/2fb4fc09356073df012869f5).
2. Clone this repository to your local computer like you would do for any other GitHub repository. 
3. If you are using an Onshape Enterprise account, open `Analyzer.py` and change the `base` URL on line 24 to the URL of your Enterprise account (e.g., `'https://ptc.onshape.com'`). 
4. Follow the instructions of [section 2 of this guide](https://github.com/PTC-Education/Onshape-Integration-Guides/blob/main/API_Intro.md#2-generating-your-onshape-api-keys) to create your API keys if you have not done so. 
5. Optional: rename the file that stores your API key to `OnshapeAPIKey.py` and put it into the folder that host this project. This file name has been added to `.gitignore`, so it won't be shared through any git commands. If you choose not to do so, you can also manually enter your API keys when you launch the app. 
6. This repository already contains a set of HTTPS certificates. You can simply use the ones we provide, or you can also create your own, following [section 3 of this guide](https://github.com/PTC-Education/Onshape-Integration-Guides/blob/main/Flask_Intro.md#3-configure-flask-as-https). Either way, you should still follow the steps of that section to add the certificates to be a trusted certificate for your computer and launch the app in your browser for testing. 
7. Follow [section 4.1 of this guide](https://github.com/PTC-Education/Onshape-Integration-Guides/blob/main/Flask_Intro.md#41-onshape-integration-through-oauth) to integrate this app to Onshape through OAuth. 

For the "Action URL" of your OAuth application extension, use the following: 

    https://127.0.0.1:5000/login?documentId={$documentId}&workspaceId={$workspaceId}&elementId={$elementId}

Then, you can simply launch the Flask app in your local computer environment with the following command lines and use it in your Onshape document: 

    $ export FLASK_APP=Analyzer
    $ export FLASK_ENV=development 
    $ flask run --cert=cert.pem --key=key.pem 

Below shows how the Flask app should be running: 

![GIF](/assets/Flask.gif)
