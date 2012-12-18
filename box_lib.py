#/!/usr/bin/env python
#-*- coding: utf-8 -*-

#This lib provides a very easy and basic implementation of the Box.net API for
#Python. It's released under the terms and conditions of GPL3.

import os
import pickle
import requests
import simplejson as json
from xml.dom.minidom import parseString


class ReadXML:
    def __init__(self):
        pass

    def parseString(self, xml, tag):
        dom = parseString(xml)
        xmlTag = dom.getElementsByTagName('{0}'.format(tag))[0].toxml()
        xmlData = xmlTag.replace('<{0}>'.format(tag),'').replace('</{0}>'.format(tag),'')

        return xmlData



class UrlRequest:
    def __init__(self):
        pass

    def request_from_url(self, url):
        req = requests.get(url)
        result = req.content

        return result



class BoxNetAuth:
    # set a standard api_key if you want to, or just set it by calling the
    # function made for this!
    def __init__(self, api_key="", token_path="box_auth.token"):

        self._API_KEY = api_key
        self._SAVE_PATH = token_path
        self._TICKET = None
        self._TICKET_LINK = "https://www.box.com/api/1.0/rest?action=get_ticket&api_key="
        self._AUTH_TICKET_LINK = "https://www.box.com/api/1.0/auth/"

        self.xmlreader = ReadXML()
        self.request = UrlRequest()


    def set_api_key(self, api_key):
        """
        After setting up a client instance, set a api key for auth
        """
        if api_key:
            self._API_KEY = api_key


    def set_settings_path(self, path):
        """
        Change the destination the auth and settings are saved to
        """
        if path:
            self._SAVE_PATH = path


    def auth_user_part1(self):
        """
        Part1 gets ticket from box.net and opens auth webpage, after this step
        you have to run "auth_user_part2" for example by clicking a button on UI
        """

        try:
            # Get a ticket for auth process
            status, ticket = self._get_ticket()
            print "Ticket status: "+status
            print "Ticket: "+ticket
            self._TICKET = ticket
        except:
            print """
            An error occured while getting a valid ticket for auth process!\n
            Check your internet connection and your user data!
            """

        if status == "get_ticket_ok":
            self._open_auth_website(ticket)
        else:
            print "Box.net API returned a bad status - something went wrong, check your data and connection!"

        # JUST A PURE CONSOLE IMPLEMENTATION - PART2 HAVE TO BE RUN FROM UI!
        #raw_input("Press Return after registration!")
        #self.auth_user_part2(ticket)


    def auth_user_part2(self):
        """
        Part2 gets the auth_token after allowing access to Box.net and saves it!
        """
        # Get auth token
        auth_url = "https://www.box.com/api/1.0/rest?action=get_auth_token&api_key={0}&ticket={1}".format(self._API_KEY, self._TICKET)
        print "Auth URL = "+auth_url
        result = self.request.request_from_url(auth_url)
        auth_token = self.xmlreader.parseString(result, "auth_token")

        print auth_token

        with open(self._SAVE_PATH, "w") as f:
            print "Save auth token to file"
            f.write(auth_token)
            print "Done"

    def _get_ticket(self):
        """
        Getting the ticket for auth-process
        """
        # request a ticket from box.net
        ticket_url = self._TICKET_LINK+self._API_KEY
        result = self.request.request_from_url(ticket_url)

        # read ticket and status from XML
        status = self.xmlreader.parseString(result, "status")
        ticket = self.xmlreader.parseString(result, "ticket")

        return status, ticket


    def _open_auth_website(self, ticket):
        """
        Just opens the auth-website in the webbrowser
        """
        # create weblink and open it up
        url = self._AUTH_TICKET_LINK+ticket

        try:
            import webbrowser
            webbrowser.open(url)
        except:
            "Can't open a webbrowser instance - sorry!"

        # just for Nokia N9's MeeGo 1.2 Harmattan
        #os.popen("/usr/bin/grob {0}".format(url))



class BoxNetClient:
    def __init__(self, api_key, settings_path="box_auth.token"):

        self.xmlreader = ReadXML()
        self.request = UrlRequest()

        self._SETTINGS_PATH = settings_path
        self._API_KEY = api_key
        self._AUTH_TOKEN = None

        if os.path.isfile(self._SETTINGS_PATH):
            with open(self._SETTINGS_PATH) as settings:
                token = settings.read()
                self._AUTH_TOKEN = token
                print "Your token is: "+self._AUTH_TOKEN
        else:
            print "WARNING: Couldn't load the token file. Check your paths and be sure you've run auth process!"


    def get_token(self):
        return self._AUTH_TOKEN


    def search_content(self, search, folder_id="0"):
        """
        Searches given phrase and returns the id of the folder/file, if not set
        it searches in root folder
        """
        url = "https://www.box.com/api/2.0/folders/{0}".format(folder_id)
        headers = {"Authorization" : "BoxAuth api_key={0}&auth_token={1}".format(self._API_KEY, self._AUTH_TOKEN)}

        req = requests.get(url, headers=headers)
        result = req.content

        # Implementierung einer Suche!
        j = json.loads(result)
        j = j["item_collection"]["entries"]
        print type(j)

        for i in j:
            if search in i["name"]:
                print "I found "+i["name"]+" with id: %s" %i["id"]


    def upload_file(self, path):
        url = "https://www.box.com/api/2.0/files/content"
        headers = {"Authorization" : "BoxAuth api_key={0}&auth_token={1}".format(self._API_KEY, self._AUTH_TOKEN)}
        data = {"folder_id" : "0"}
        files = {"file": open(path, "rb")}
        req = requests.post(url, headers=headers, data=data, files=files)
        print req.content


    def delete_file(self, file_id):
        url = "https://api.box.com/2.0/files/"+file_id
        headers = {"Authorization" : "BoxAuth api_key={0}&auth_token={1}".format(self._API_KEY, self._AUTH_TOKEN)}
        req = requests.delete(url, headers=headers)


if __name__ == "__main__":
    BoxNetClient()
    print "IT'S NOT RECOMMEND TO USE THIS STAND ALONE - IT'S A LIB!"
