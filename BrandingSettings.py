from tkinter import StringVar
import json

class BrandingSettings:
    def __init__(self, json=None):
        self.name = StringVar()
        self.headerBgColor = StringVar()
        self.menuIconColor = StringVar()
        self.nameColor = StringVar()
        self.statusBarColor = StringVar()

        if json:
            self.id = json["id"]
            self.iconId = json["iconId"]
            self.name.set(json["brandingName"])
            self.headerBgColor.set(json["headerBackgroundColorCode"])
            self.menuIconColor.set(json["menuIconColorCode"])
            self.nameColor.set(json["brandingNameColorCode"])
            self.statusBarColor.set(json["statusBarTextColor"])

    def set(self, json):
        self.id = json["id"]
        self.name.set(json["name"])
        self.headerBgColor.set(json["headerBackgroundColorCode"])
        self.menuIconColor.set(json["menuIconColorCode"])
        self.nameColor.set(json["brandingNameColorCode"])
        self.statusBarColor.set(json["statusBarTextColor"])

    def createPayload(self):
        return json.dumps({
            "brandingName": self.name.get(),
            "iconId": self.iconId,
            "headerBackgroundColorCode": self.headerBgColor.get(),
            "menuIconColorCode": self.menuIconColor.get(),
            "brandingNameColorCode": self.nameColor.get(),
            "statusBarTextColor": self.statusBarColor.get()
        })
