![banner](https://raw.githubusercontent.com/dtmilano/lex-bot-tester/master/images/pexels-photo-595804-wide.jpeg)

# lex-bot-tester
**AWS Lex Bot Tester** is a library that simplifies the creation of Amazon Alexa Skills and AWS Lex Bot functional tests.

While this framework has been developed in python (*Node version in in the roadmap*) it can be used to test Skills and Bots developed in any language.

Using AWS Lex Models Client this utility inspects the properties of the available Bots and creates specific Results classes to be used by the tests.

Certainly, there are ways of testing your bots using AWS CLI as explained in [Test the Bot Using Text Input (AWS CLI)](http://docs.aws.amazon.com/lex/latest/dg/gs-create-test-text.html) but **lex-bot-tester** provides a more concise, type safe and object oriented way of doing it.

# Installation
Run

    pip install lex-bot-tester
    

# Examples

## Alexa Skill test example
This example uses Alexa Skill Blueprint: BookMyTrip.

Using **lex-bot-tester** conversational tests like the following one can be created with minimal effort.

```python
class AlexaSkillManagementClientTests(AlexaSkillTest):

    def test_book_my_trip_reserve_a_car(self):
        skill_name = 'BookMyTripSkill'
        intent = 'BookCar'
        conversation = [
            {'slot': None, 'text': 'ask book my trip to reserve a car'},
            {'slot': 'CarType', 'text': 'midsize'},
            {'slot': 'PickUpCity', 'text': 'buenos aires'},
            {'slot': 'PickUpDate', 'text': 'tomorrow'},
            {'slot': 'ReturnDate', 'text': 'five days from now'},
            {'slot': 'DriverAge', 'text': 'twenty five'},
            {'slot': None, 'prompt': 'Confirmation', 'text': 'yes'}
        ]
        self.conversation_text(skill_name, intent, conversation, verbose=True)
```

you can see full source code at [alexaskillmanagementclienttests.py](https://github.com/dtmilano/lex-bot-tester/blob/master/tests/com/dtmilano/aws/alexa/alexaskillmanagementclienttests.py).

### Running the tests
You can run the tests from your favorite IDE or from the command line.

If you are interested in seeing the details of the conversation you can add the `--verbose` option to the test runner.

```
$ ./alexaskillmamagementclienttests.py --verbose
```

and you will see an interaction similar to this one

![test run](https://cdn-images-1.medium.com/max/1200/1*QO_6uZSVzY_BRGKIWZid4g.png)

## AWS Lex Bot test example
You may be familiar with this kind of tests in the *AWS Lex Console* (this example uses the well know *OrderFlowers* bot).

![test-bot](https://raw.githubusercontent.com/dtmilano/lex-bot-tester/master/images/test-bot.png)

> More information about these manual tests using the console can be found [here](http://docs.aws.amazon.com/lex/latest/dg/gs2-build-and-test.html)

However, once you have the **lex-bot-tester** installed, you can create tests like this one:

```python
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Lex Bot Tester
    Copyright (C) 2017  Diego Torres Milano

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re
import unittest

from lex_bot_tester.aws.lex.conversation import Conversation, ConversationItem
from lex_bot_tester.aws.lex.lexbottest import LexBotTest
from lex_bot_tester.aws.lex.lexmodelsclient import LexModelsClient
from lex_bot_tester.aws.lex.lexruntimeclient import DialogState

RE_DATE = re.compile('\d+-\d+-\d+')

BOT_NAME = 'OrderFlowers'
BOT_ALIAS = 'OrderFlowersLatest'
USER_ID = 'ClientId'


class OrderFlowersTests(LexBotTest):
    def test_conversations_text(self):
        lmc = LexModelsClient(BOT_NAME, BOT_ALIAS)
        conversations = []
        for i in lmc.get_intents_for_bot():
            r = lmc.get_result_class_for_intent(i)
            if i == 'OrderFlowers':
                conversations.append(Conversation(
                    ConversationItem('I would like to order some roses',
                                     r(DialogState.ELICIT_SLOT, flower_type='roses')),
                    ConversationItem('white', r(DialogState.ELICIT_SLOT, flower_type='roses', flower_color='white')),
                    ConversationItem('next Sunday',
                                     r(DialogState.ELICIT_SLOT, flower_type='roses', flower_color='white',
                                       pickup_date=RE_DATE)),
                    ConversationItem('noon', r(DialogState.CONFIRM_INTENT, flower_type='roses', flower_color='white',
                                               pickup_date=RE_DATE, pickup_time='12:00')),
                    ConversationItem('yes', r(DialogState.FULFILLED, flower_type='roses', flower_color='white',
                                              pickup_date=RE_DATE, pickup_time='12:00')),
                ))
            elif i == 'Cancel':
                conversations.append(Conversation(
                    ConversationItem('Cancel', r(DialogState.READY_FOR_FULFILLMENT))
                ))
        self.conversations_text(BOT_NAME, BOT_ALIAS, USER_ID, conversations)


if __name__ == '__main__':
    unittest.main()
```

This test, first creates a `LexModelsClient` to inspect the definitions of the bot, its intents and slots to later use a class factory that defines specific classes for each intent which are obtained by `get_result_class_for_intent(i)`.

This result class reference, which extends `ResultBase` class is assigned to the variable `r` for convenience. Then, for each intent, a `Conversation`, consisting of a list of `ConversationItems` is created.

`ConversationItem` specifies the text or utterance sent and the expected result, using the `r` class reference and invoking the constructor with the expected `DialogState` and the values of the `slots`.

`pickup_date` is a particular case, as it is selected as `next Sunday` so instead of looking for a particular value we are checking if it matches a regular expression defining dates.

Finally, once the `conversation` list is completed, a call to the helper method `conversations_text` providing this list as an argument completes the test.

However, if you are more into a data-driven approach, you can also declare the conversation as a data structure as shown in the following example.

```python
    def test_conversations_text_book_car(self):
        bot_name = 'BookTrip'
        bot_alias = 'BookTripLatest'
        user_id = 'ClientId'
        conversation_definition = {
            'BookCar': [
                ('book a car', DialogState.ELICIT_SLOT, {}),
                ('L.A.', DialogState.ELICIT_SLOT, {}),
                ('next week', DialogState.ELICIT_SLOT, {'PickUpDate': RE_WEEK}),
                ('a month from now', DialogState.ELICIT_SLOT, {'ReturnDate': RE_DATE}),
                ('25', DialogState.ELICIT_SLOT, {}),
                ('economy', DialogState.CONFIRM_INTENT, {}),
                ('yes', DialogState.READY_FOR_FULFILLMENT, {}),
            ],
            'Cancel': [
                ('cancel', DialogState.READY_FOR_FULFILLMENT, {})
            ]
        }
        self.conversations_text_helper(bot_alias, bot_name, user_id, conversation_definition, verbose)
```

Both approaches are identical in functionality, so you can choose the one that suits your taste.

## Result classes
As mentioned before, `LexModelsClient.get_result_class_for_intent(intent)` returns the class that represents the response result once the Bot is invoked using the corresponding utterance.

The signature of the constructor matches this pattern

    class MyIntentResult(ResultBase):
        def __init__(dialog_state, **kwargs):
            ...
            

To comply with [PEP 8](https://www.python.org/dev/peps/pep-0008/#prescriptive-naming-conventions), keyword args representing slots are named using *snake case* when usually slots are named using *camel case*. Then, for example, the slot `FlowerType` will be represented by its corresponding keyword arg `flower_type`.

### Conversations
**Conversation** is a list of **ConversationItems**. These **ConversationItems** represent the *send* -> *response* interaction. 

    class ConversationItem(object):
        
        def __init__(self, send, receive):
            ...

Perhaps, taking a look at [lexbottestertests.py](https://github.com/dtmilano/lex-bot-tester/blob/master/tests/com/dtmilano/aws/lex/lexbottesttests.py) clarifies the idea. That test, uses the same structure and the classes created by inspecting the models for two different Bots: OrderFlowers and BookTrip.

### Running the tests
You can run the tests from your favorite IDE or from the command line.

If you are interested in seeing the details of the conversation you can add the `--verbose` option to the test runner.

```
$ ./lexbottesttests.py --verbose
```

and you will see an interaction similar to the one presented before.

![term-output](https://raw.githubusercontent.com/dtmilano/lex-bot-tester/master/images/term-output.png)

# Resources
* [Testing Alexa Skills - The grail quest](https://medium.com/@dtmilano/testing-alexa-skills-the-grail-quest-3beba82450bb)
* [Creating conversational AWS Lex Bot tests](https://medium.com/@dtmilano/creating-conversational-aws-lex-bot-tests-da84a83fe688)
* [Improving conversational AWS Lex Bot tests](https://medium.com/@dtmilano/improving-conversational-aws-lex-bot-tests-6d041437a05f)
