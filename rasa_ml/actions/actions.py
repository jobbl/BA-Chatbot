from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from emotion_detection import emotion_detection_ml



class ReactionPast(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_past'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_past')
        print(msg)
        # dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotion = emotion_detection_ml(msg)

        if emotion == "excited":
            response = "I am glad to hear that you had a good time! Keep up the good work!"
        if emotion == "tranquil":
            response = "Relaxing times are a blessing. Thats what our planet needs in times like these!"
        if emotion == "rooted":
            response = "That sounds balanced. Life has a way of keeping us in the middle, it seems to me."
        if emotion == "empty":
            response = "Everyone feels drawn out from time to time, because we have limited energy to spend. Do not hesitate to be kind to yourself and reach out when you feel low."
        if emotion == "threatened":
            response = "Sounds like you had some stressful time. Life can seem a scary place. I understand. Maybe some time in nature could show you the gentle sides of life again."

        dispatcher.utter_message(text=response)

        return [SlotSet("journal_past", None)]

class ReactionNow(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_now'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_now')
        print(msg)
        # dispatcher.utter_message(text= msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotion = emotion_detection_ml(msg)

        if emotion == "excited":
            response = "Yeah, you are radiating! Thanks for sharing that with me, your happiness is contagious!"
        if emotion == "tranquil":
            response = "Being calm is a very balanced kind of happiness. Enjoy!"
        if emotion == "rooted":
            response = "Feeling neutral is a very natural feeling. From here you can see the mountains and the sea!"
        if emotion == "empty":
            response = "Let me give you a virtual hug my friend. Sadness is like the tides, it comes and goes."
        if emotion == "threatened":
            response = "Sounds like you are worrying quite a bit. It is totally understandable, many people are stressed these days about the superficial expectation of society. Being stressed helps no one. Take some deep breaths. Relax your shoulders. Visit Nature today, it will make you feel better."
       
        dispatcher.utter_message(text=response)

        return [SlotSet("journal_now", None)]

class ReactionFuture(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_future'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_future')
        print(msg)
        # dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))
        emotion = emotion_detection_ml(msg)

        if emotion == "excited":
            response = "Sounds like great times are ahead! I wish i could come with you. All the best on your adventures."
        if emotion == "tranquil":
            response = "I am so happy that you have a relaxed outlook. Go and share some of that wisdom, when you feel like it!"
        if emotion == "rooted":
            response = "The future is full of possibility. I hope yours brings you only pleasant surprises. But whatever comes, it will make you grow."
        if emotion == "empty":
            response = "Nobody has found the best plan to live a life. Enjoy the little things and listen. Finding happiness is not a straight line, maybe it hides behind the next corner."
        if emotion == "threatened":
            response = "Even if the future looks stressful, it only is stressful as long as you nurture the reason for the stress. Maybe take a little break from worrying from time to time, spend time in nature or listening to music. It might open new perspectives."

        dispatcher.utter_message(text=response)

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