from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from emotion_detection import emotion_detection_ml, emotion_detection_rule



class ReactionPast(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_past'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_past')
        print(msg)
        # dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotions = {"ml":emotion_detection_ml(msg),"rule":emotion_detection_rule(msg)}
        response = {}

        for model in emotions:
            if emotions[model] == "excited":
                response[model] = "I am glad to hear that you had a good time! Keep up the good work!"
            if emotions[model] == "tranquil":
                response[model] = "Relaxing times are a blessing. Thats what our planet needs in times like these!"
            if emotions[model] == "rooted":
                response[model] = "That sounds balanced. Life has a way of keeping us in the middle, it seems."
            if emotions[model] == "empty":
                response[model] = "Everyone feels drawn out from time to time, because we have limited energy to spend. Do not hesitate to be kind to yourself and reach out when you feel low."
            if emotions[model] == "threatened":
                response[model] = "Sounds like you had some stressful time. Life can seem a scary place. I understand. Maybe spending some time in nature could show you the gentle sides of life again."

        dispatcher.utter_message(json_message={"ml":response["ml"]})
        dispatcher.utter_message(json_message={"rule":response["rule"]})


        return [SlotSet("journal_past", None)]

class ReactionNow(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_now'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_now')
        print(msg)
        # dispatcher.utter_message(text= msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotions = {"ml":emotion_detection_ml(msg),"rule":emotion_detection_rule(msg)}
        response = {}

        for model in emotions:
            if emotions[model] == "excited":
                response[model] = "Yeah, you are radiating! Thanks for sharing that with me, your happiness is contagious!"
            if emotions[model] == "tranquil":
                response[model] = "Being calm is a very balanced kind of happiness. Enjoy!"
            if emotions[model] == "rooted":
                response[model] = "Feeling neutral is a very natural feeling. From here you can see the mountains and the sea!"
            if emotions[model] == "empty":
                response[model] = "Let me give you a virtual hug my friend. Sadness is like the tides, it comes and goes."
            if emotions[model] == "threatened":
                response[model] = "Sounds like you are worrying quite a bit. It is totally understandable, many people are stressed these days about the superficial expectation of society. Being stressed helps no one. Take some deep breaths. Relax your shoulders. Visit Nature today, it will make you feel better."
       
        dispatcher.utter_message(json_message={"ml":response["ml"]})
        dispatcher.utter_message(json_message={"rule":response["rule"]})

        return [SlotSet("journal_now", None)]

class ReactionFuture(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_future'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_future')
        print(msg)
        # dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotions = {"ml":emotion_detection_ml(msg),"rule":emotion_detection_rule(msg)}
        response = {}

        for model in emotions:
            if emotions[model] == "excited":
                response[model] = "Sounds like great times are ahead! I wish i could come with you. All the best on your adventures."
            if emotions[model] == "tranquil":
                response[model] = "I am so happy that you have a relaxed outlook. Go and share some of that wisdom, when you feel like it!"
            if emotions[model] == "rooted":
                response[model] = "The future is full of possibility. I hope yours brings you only pleasant surprises. But whatever comes, it will make you grow."
            if emotions[model] == "empty":
                response[model] = "Nobody has found the best plan to live a life. Enjoy the little things and listen. Finding happiness is not a straight line, maybe it hides behind the next corner."
            if emotions[model] == "threatened":
                response[model] = "Even if the future looks stressful, it only is stressful as long as you nurture the reason for the stress. Maybe take a little break from worrying from time to time, spend time in nature or listen to music. It might open new perspectives."

        dispatcher.utter_message(json_message={"ml":response["ml"]})
        dispatcher.utter_message(json_message={"rule":response["rule"]})

        return [SlotSet("journal_future", None)]

class ActionRepeat(Action):
    
    def name(self) -> Text:
        return "action_repeat"

    def run(self, dispatcher, tracker, domain):

        if len(tracker.events) >= 3:
            i = 0
            while(tracker.events[i].get('event')!='bot' ):
                i = i-1
            last = tracker.events[i] #I have custom response
            dispatcher.utter_message(text=last.get('text'))
        return []