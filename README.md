# transloc-skill
Alexa skill for Duke Bus times.

## To run locally:

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

## How to use the skill

At this point, you'll have a running developer build. On your personal Alexa or through the developer console you can say things like:

- Launch Blue Devil Buses
- Ask Blue Devil Buses for West Campus Bus Stop

to request information. I've built out a really primitive interaction model that gives information for a certain stop. You can also deploy to AWS. There's a pretty good tutorial [here](https://developer.amazon.com/blogs/post/8e8ad73a-99e9-4c0f-a7b3-60f92287b0bf/New-Alexa-Tutorial-Deploy-Flask-Ask-Skills-to-AWS-Lambda-with-Zappa) that'll get you most of the way there. 

I've already deployed the skill to the store under the utterance "Duke Bus Times." Feel free to check it out!

## Roadmap

I'm not sure how much work I'll put into this. In it's current state it serves its purposes pretty well. In the future it might be fun to build out some of the following features.

- Alarm (e.g. notify me when a bus is 3 minutes from the stop..)
- Default stop settings (Amazon doesn't let you store information across sessions. I think this would involve a custom database w/ userID's and user preferences which is more trouble than it's worth.)
- Nearest stops, right now the skill just has a hand-selected list of popular stops. It might be more useful to grab the Alexa's location using the Device Address API and list the nearest stops. 
- More Transit agencies, right now the skill is bespoke to Duke transit. It would be trivial to add more schools or generalize the app, but this would complicate the interaction model. 


