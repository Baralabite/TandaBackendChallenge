"""
The MIT License (MIT)

Copyright (c) 2016 John Board

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re

class RequestEventManager:
    """
    Static class to handle event listeners, and event calls

    Place the decorator:
    @RequestEventManager.addListener(regex, method)
    before a function you want to use as a callback for
    a certain URL (as specified by the regex).

    Then when callEvent(url, method) is called, if the url and method
    match any regex, it calls the associated callback.
    """

    listeners = {}

    def addListener(regex, method="GET"):
        """
        Decorator for listener callback functions
        :param regex: String/List regex or list of regexes
        :param method: POST/GET
        :return:
        """
        def inner(callback):
            """
            Inner wrapper for callbacks. Adds function to RequestEventManager.listeners
            :param callback: Function to callback
            :return:
            """

            #Normalizes the input. If not a list, makes it a list.
            regexList = [regex] if not type(regex) == list else regex

            #Adds the regex to listeners
            for regex_ in regexList:
                #If the regex isn't in the listeners yet, create a dictionary (for the different methods)
                if not regex_ in RequestEventManager.listeners:
                    RequestEventManager.listeners[regex_] = {}
                #Adds the listener to the specific regex AND method
                RequestEventManager.listeners[regex_][method] = callback
        return inner

    def callEvent(url, method="GET"):
        """
        Calls the event with the specified URL and method
        :param url:
        :param method:
        :return:
        """

        #Checks all the regexes
        for regex in RequestEventManager.listeners:
            #If the method doesn't match, then keep looking
            if not method in RequestEventManager.listeners[regex]:
                continue

            #If it finds a matching method and URL, then call the function, with the regex data as the parameter
            finds = re.findall(regex, url)
            if len(finds) > 0:
                return RequestEventManager.listeners[regex][method](finds)
        #Else the URL listener doesn't exit - 404!
        return "[]", 404