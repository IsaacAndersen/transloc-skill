# transloc-skill
Alexa skill for Duke Bus times.

To run locally:

Launch the Flask server: 
```
python server.py
```
To start a HTTP tunnel on port 5000, run this next:
```
./ngrok http 5000
```
Use the generated https address as your endpoint in the Alexa skill dashboard.

```
Session Status                online                                            
Session Expires               6 hours, 1 minute                                 
Version                       2.2.8                                             
Region                        United States (us)                                
Web Interface                 http://127.0.0.1:4040                             
Forwarding                    http://<sessionid>.ngrok.io -> localhost:5000        
Forwarding                    https://<sessionid>.ngrok.io -> localhost:5000  
```
