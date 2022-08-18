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
        dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))

        return [SlotSet("journal_past", None)]

class ReactionNow(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_now'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_now')
        print(msg)
        dispatcher.utter_message(text= msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))

        return [SlotSet("journal_now", None)]

class ReactionFuture(Action):
    def name(self) -> Text:
        return 'action_utter_reaction_future'


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        msg = tracker.get_slot('journal_future')
        print(msg)
        dispatcher.utter_message(text=msg + " --> ML-based: " + emotion_detection_ml(msg) + ", Rule-based: " + emotion_detection_rule(msg))

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