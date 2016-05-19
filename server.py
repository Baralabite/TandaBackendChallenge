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

from http.server import BaseHTTPRequestHandler, HTTPServer
from storage import *
from event import *
import re, json
import datetime, calendar

class TandaHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    This is a pretty basic HTTP Request Handler as desired by the BaseHTTPServer
    It calls the event handler with the URL and the request method
    It also then ships the data returned by the url's specific function back to the client.
    """
    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self, *args):
        """
        Handles GET requests
        """
        message, response = RequestEventManager.callEvent(self.path, method="GET")

        self.send_response(response)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))


    def do_POST(self, *args):
        """
        Handles POST requests
        """
        message, response = RequestEventManager.callEvent(self.path, method="POST")

        self.send_response(response)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

class TimeclockEndpoint:
    """
    TimeclockEndpoint: This handles the requests sent to the HTTP server.
    It works on a callback system, whereby a listener is addded on a function-by-function
     basis.

    To add a listener, use a decorator with the syntax of:
    @RequestEventManager.addListener([regex], method="POST"/"GET")

    When a URL that matches the specified regex(es) gets requested, the event manager
    calls the callback associated with that listener.

    The function should return the data to be sent back to the client, as well as the return
    code. (200/404, etc)
    """

    data = FileHandler()

    @RequestEventManager.addListener("/clear_data", method="POST")
    def clearData(regexData):
        """
        Handles /clear_data request. Clears dictionary and saves to file.
        :param regexData:
        :return:
        """
        TimeclockEndpoint.data.clear()
        TimeclockEndpoint.data.save()
        return "", 200

    @RequestEventManager.addListener("^/(.*?)/(.*?)$", method="POST")
    def addClockEntry(regexData):
        """
        Handles posts of /:device/:timestamp
        :param regexData:
        :return:
        """
        itemID, time = regexData[0]

        if not itemID in TimeclockEndpoint.data:                #If no entries have yet been made to this device,
            TimeclockEndpoint.data[itemID] = [int(time)]        #Create an entry, add a list with the first value in it
        else:
            TimeclockEndpoint.data[itemID].append(int(time))    #Else ajust add to the list

        TimeclockEndpoint.data.save()                           #Once the data dictionary has been modified, save it

        return "", 200

    @RequestEventManager.addListener("/devices", method="GET")
    def getDevices(regexData):
        """
        Returns all the current device entries, and their timestamps
        :param regexData:
        :return:
        """
        message = json.dumps(TimeclockEndpoint.data)
        return message, 200

    #Matches all the "ping" gets
    @RequestEventManager.addListener(["^/(all)/(.{10})$",
                                   "^/(.{36})/(.{10})$",
                                   "^/(all)/(.{10})/(.{10})$",
                                   "^/(.{36})/(.{10})/(.{10})$"], method="GET")
    def getClockEntry(regexData):
        """
        Handles combination of ping requests
        :param regexData:
        :return:
        """
        if len(regexData[0]) == 2:              #If only a "from_" was specified,
            deviceID, time_from = regexData[0]
            time_to = None
        else:                                   #Else if both were specified,
            deviceID, time_from, time_to = regexData[0]

        #Request list of pings
        pings = TimeclockEndpoint.getPings(deviceID, time_from, to=time_to)

        #Send them back to requester
        message = json.dumps(pings)
        return message, 200


    def getPings(device, from_, to=None):
        """
        Helper function to aid in the getting of the pings for devices between certain
        timestamps.
        :param device:
        :param from_:
        :param to:
        :return:
        """
        def parseTime(time_):
            """
            Function to convert from UTC time to unix timestamp
            :param time_:
            :return:
            """
            try:
                return int(time_)
            except:
                return calendar.timegm(datetime.datetime.strptime(time_, "%Y-%m-%d").timetuple())

        #Parse the from_ time and the to time. If to is None, set it to
        #from_ + 24h (86400 seconds)
        from_ = parseTime(from_)
        to = parseTime(to) if to else from_ + 86400


        if device == "all":                                 #If caller wants all the devices, then...
            times = {}
            for device in TimeclockEndpoint.data:           #Iterate over the devices, and add them to times
                times[device] = []
                for i in TimeclockEndpoint.data[device]:    #Iterate over pings. If pings within the time specified...
                    if i >= from_ and i <= to:
                        times[device].append(i)
            return times

        elif not device in TimeclockEndpoint.data:          #If the device doesn't exist, return empty list
            return []

        else:                                               #If a proper device was specified...
            times = []
            for i in TimeclockEndpoint.data[device]:        #Then iterate over it's pings, and add
                if i >= from_ and i < to:
                    times.append(i)
            return times

if __name__ == "__main__":
    server_address = ('127.0.0.1', 3000)

    httpd = HTTPServer(server_address, TandaHTTPRequestHandler)
    httpd.serve_forever()