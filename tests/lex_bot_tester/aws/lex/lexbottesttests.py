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
import sys
import unittest

from lex_bot_tester.aws.lex.conversation import Conversation, ConversationItem
from lex_bot_tester.aws.lex.lexbottest import LexBotTest
from lex_bot_tester.aws.lex.lexmodelsclient import LexModelsClient
from lex_bot_tester.aws.lex.lexruntimeclient import DialogState

RE_DATE = re.compile('\d+-\d+-\d+')
RE_WEEK = re.compile('\d+-w\d+')

verbose = False


class LexBotTestTests(LexBotTest):
    def test_conversations_text_order_flowers(self):
        bot_name = 'OrderFlowers'
        bot_alias = 'OrderFlowersLatest'
        user_id = 'ClientId'
        lmc = LexModelsClient(bot_name, bot_alias)
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
        self.conversations_text(bot_name, bot_alias, user_id, conversations, verbose=verbose)

    def test_conversations_text_book_car(self):
        bot_name = 'BookTrip'
        bot_alias = 'BookTripLatest'
        user_id = 'ClientId'
        conversation_definition = {
            'BookCar': [
                ('reserve a car', DialogState.ELICIT_SLOT, {}),
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
        self.conversations_text_helper(bot_alias, bot_name, user_id, conversation_definition, verbose, False)

    def test_conversations_text_book_hotel_tts(self):
        bot_name = 'BookTrip'
        bot_alias = 'BookTripLatest'
        user_id = 'ClientId'
        conversation_definition = {
            'BookHotel': [
                ('book a three night stay in London', DialogState.ELICIT_SLOT, {'Location': 'London'}),
                ('next Monday', DialogState.ELICIT_SLOT, {'CheckInDate': RE_DATE}),
                ('king', DialogState.CONFIRM_INTENT, {}),
                ('yes', DialogState.READY_FOR_FULFILLMENT, {}),
            ],
            'Cancel': [
                ('cancel', DialogState.READY_FOR_FULFILLMENT, {})
            ]
        }
        self.conversations_text_helper(bot_alias, bot_name, user_id, conversation_definition, verbose, True)


if __name__ == '__main__':
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    unittest.main()
