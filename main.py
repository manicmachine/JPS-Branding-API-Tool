# © 2022 Jamf Software, LLC
# THE SOFTWARE IS PROVIDED "AS-IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL JAMF SOFTWARE, LLC OR
# ANY OF ITS AFFILIATES BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OF OR OTHER DEALINGS IN THE SOFTWARE, INCLUDING BUT NOT LIMITED
# TO DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES AND OTHER
# DAMAGES SUCH AS LOSS OF USE, PROFITS, SAVINGS, TIME OR DATA, BUSINESS INTERRUPTION, OR
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES.

import requests
from tkinter import *
from tkinter import ttk
from tkinter.colorchooser import askcolor
from datetime import datetime
from JpsSettings import *
from BrandingSettings import *

# State
jpsSettings = None
selectedId = None
currentBranding = None
brandingIds = []
brandings = []
tokenUrlTemplate = "https://{}/api/auth/tokens"
brandingGetUrlTemplate = "https://{}/api/v1/self-service/branding/ios"
brandingPutUrlTemplate = "https://{}/api/v1/self-service/branding/ios/{}"
brandingReqHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}"
}

# UI Elements
root = None

hostnameEntry = None
usernameEntry = None
passwordEntry = None
brandingNameEntry = None
headerBackgroundColorEntry = None
menuIconColorEntry = None
brandingNameColorEntry = None
loggingField = None

selectBrandingCombobox = None

headerBackgroundColorPicker = None
menuIconColorPicker = None
brandingNameColorPicker = None
lightRadioButton = None
darkRadioButton = None
submitButton = None

# Methods
def isAuthenticated():
    return jpsSettings.token and datetime.now().timestamp() < jpsSettings.expires


def authenticate():
    consoleLog("Authenticating to {} as {}".format(jpsSettings.hostname.get(), jpsSettings.username.get()))

    try:
        res = requests.post(tokenUrlTemplate.format(jpsSettings.hostname.get()),
                        auth=requests.auth.HTTPBasicAuth(jpsSettings.username.get(), jpsSettings.password.get()))
        if res:
            consoleLog("Authentication successful")
            jpsSettings.token = res.json()["token"]
            jpsSettings.expires = res.json()["expires"]

            brandingReqHeaders["Authorization"] = brandingReqHeaders["Authorization"].format(jpsSettings.token)
        else:
            consoleLog("Authentication failed, HTTP code {}".format(res.status_code))
            consoleLog(res.json())

        return res
    except requests.ConnectionError:
        consoleLog("Authentication failed, unable to connect to {}".format(jpsSettings.hostname.get()))


def retrieveBrandingIdsAndUpdate():
    global currentBranding

    if isAuthenticated() or authenticate():
        consoleLog("Retrieving iOS brandings")
        res = requests.get(brandingGetUrlTemplate.format(jpsSettings.hostname.get()),
                           headers=brandingReqHeaders)

        if res:
            consoleLog("Brandings retrieved")
            for branding in res.json()["results"]:
                brandingIds.append(branding["id"])
                brandings.append(BrandingSettings(branding))

            selectBrandingCombobox['values'] = brandingIds
            selectBrandingCombobox.current(0)

            update()
        else:
            consoleLog("Retrieval failed, HTTP code {}: {} - {}".format(res.status_code, res.json()["errors"][0]["code"], res.json()["errors"][0]["description"]))


def putBrandingSettings():
    global currentBranding

    consoleLog("Submitting new settings for branding id {}".format(currentBranding.id))
    res = requests.put(brandingPutUrlTemplate.format(jpsSettings.hostname.get()),
                        headers=brandingReqHeaders, data=currentBranding.createPayload())

    if res:
        consoleLog("Submission successful")
    else:
        consoleLog("Submission failed, HTTP code {}: {} - {}".format(res.status_code, res.json()["errors"][0]["code"], res.json()["errors"][0]["description"]))


def consoleLog(text):
    loggingField.configure(state=NORMAL)
    loggingField.insert(END, "{}: {}\n".format(datetime.now().strftime("%X"), text))
    loggingField.see(END)
    loggingField.configure(state=DISABLED)


def getColor(title):
    return askcolor(title=title)[1].split('#')[1].upper()


def pickHeaderColor():
    global currentBranding

    currentBranding.headerBgColor.set(getColor("Header Background Color"))
    update()


def pickMenuColor():
    global currentBranding

    currentBranding.menuIconColor.set(getColor("Menu Icon Color"))
    update()


def pickNameColor():
    global currentBranding

    currentBranding.nameColor.set(getColor("Branding Name Color"))
    update()


def update():
    global currentBranding, brandingPutUrlTemplate

    currentBranding = brandings[selectBrandingCombobox.current()]
    selectBrandingCombobox['values'] = brandingIds
    brandingPutUrlTemplate = brandingPutUrlTemplate.format(jpsSettings.hostname.get(), currentBranding.id)

    selectBrandingCombobox.configure(state="readonly")
    brandingNameEntry.configure(textvariable=currentBranding.name, state=NORMAL)
    headerBackgroundColorEntry.configure(textvariable=currentBranding.headerBgColor, state=NORMAL)
    menuIconColorEntry.configure(textvariable=currentBranding.menuIconColor, state=NORMAL)
    brandingNameColorEntry.configure(textvariable=currentBranding.nameColor, state=NORMAL)
    headerBackgroundColorPicker.configure(state=NORMAL)
    menuIconColorPicker.configure(state=NORMAL)
    brandingNameColorPicker.configure(state=NORMAL)
    lightRadioButton.configure(variable=currentBranding.statusBarColor, state=NORMAL)
    darkRadioButton.configure(variable=currentBranding.statusBarColor, state=NORMAL)
    submitButton.configure(state=NORMAL)


if __name__ == '__main__':
    root = Tk()
    root.geometry("428x700")
    root.wm_title("Jamf Pro Server iOS 14 Branding Tool")
    root.wm_resizable(False, False)

    jpsSettings = JpsSettings()
    currentBranding = BrandingSettings()
    selectedId = StringVar()

    # JPS settings panel
    jpsSettingsLabelFrame = LabelFrame(root, text="Jamf Pro Server Settings")
    jpsSettingsLabelFrame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    jpsSettingsInnerframe = Frame(jpsSettingsLabelFrame)
    jpsSettingsInnerframe.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Hostname
    jpsSettings.hostname = StringVar()
    hostnameLabel = Label(jpsSettingsInnerframe, text="Hostname")
    hostnameLabel.grid(row=0, column=0, columnspan=2, sticky="we")

    hostnameEntry = Entry(jpsSettingsInnerframe, justify=CENTER, textvariable=jpsSettings.hostname)
    hostnameEntry.grid(row=1, column=0, columnspan=2, sticky="we")

    # Username
    jpsSettings.username = StringVar()
    usernameLabel = Label(jpsSettingsInnerframe, text="Username")
    usernameLabel.grid(row=2, column=0)

    usernameEntry = Entry(jpsSettingsInnerframe, justify=CENTER, textvariable=jpsSettings.username)
    usernameEntry.grid(row=3, column=0)

    # Password
    jpsSettings.password = StringVar()
    passwordLabel = Label(jpsSettingsInnerframe, text="Password")
    passwordLabel.grid(row=2, column=1)

    passwordEntry = Entry(jpsSettingsInnerframe, show="*", justify=CENTER, textvariable=jpsSettings.password)
    passwordEntry.grid(row=3, column=1)

    # Retrieve branding button
    retrieveBrandingsButton = Button(jpsSettingsInnerframe, text="Retrieve Brandings", command=retrieveBrandingIdsAndUpdate)
    retrieveBrandingsButton.grid(row=6, column=0, columnspan=2, sticky="we", pady=10)

    # Branding settings frame
    brandingSettingsLabelFrame = LabelFrame(root, text="Branding Settings")
    brandingSettingsLabelFrame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    brandingSettingsInnerFrame = Frame(brandingSettingsLabelFrame)
    brandingSettingsInnerFrame.pack(fill=BOTH, expand=True, padx=10)

    # Selected branding id
    selectBrandingIdFrame = Frame(brandingSettingsInnerFrame)
    selectBrandingIdFrame.pack(fill=BOTH, expand=True, pady=10)

    selectBrandingLabel = Label(selectBrandingIdFrame, text="Selected Branding ID:")
    selectBrandingLabel.pack(side=LEFT)

    selectBrandingCombobox = ttk.Combobox(selectBrandingIdFrame, textvariable=selectedId, state=DISABLED, justify=RIGHT, validate="focusout", validatecommand=update)
    selectBrandingCombobox['values'] = brandingIds
    selectBrandingCombobox.pack(side=RIGHT)

    brandingSeparator = ttk.Separator(brandingSettingsInnerFrame, orient=HORIZONTAL)
    brandingSeparator.pack(fill=X, expand=True, padx=10)

    brandingSettingsFrame = Frame(brandingSettingsInnerFrame)
    brandingSettingsFrame.pack(fill=BOTH, expand=True, pady=10)
    brandingSettingsFrame.columnconfigure(0, weight=1)

    # Branding name
    brandingNameLabel = Label(brandingSettingsFrame, text="Branding Name")
    brandingNameLabel.grid(row=0, column=0, sticky="w")

    brandingNameEntry = Entry(brandingSettingsFrame, textvariable=currentBranding.name, state=DISABLED)
    brandingNameEntry.grid(row=1, column=0, columnspan=2, sticky="we")

    # Header background color
    headerBackgroundColorLabel = Label(brandingSettingsFrame, text="Header Background Color")
    headerBackgroundColorLabel.grid(row=2, column=0, sticky="w")

    headerBackgroundColorEntry = Entry(brandingSettingsFrame, textvariable=currentBranding.headerBgColor, state=DISABLED)
    headerBackgroundColorEntry.grid(row=3, column=0, sticky="we")

    headerBackgroundColorPicker = Button(brandingSettingsFrame, text="Pick Color", command=pickHeaderColor, state=DISABLED)
    headerBackgroundColorPicker.grid(row=3, column=1, sticky="e")

    # Menu icon color
    menuIconColorLabel = Label(brandingSettingsFrame, text="Menu Icon Color")
    menuIconColorLabel.grid(row=4, column=0, sticky="w")

    menuIconColorEntry = Entry(brandingSettingsFrame, textvariable=currentBranding.menuIconColor, state=DISABLED)
    menuIconColorEntry.grid(row=5, column=0, sticky="we")

    menuIconColorPicker = Button(brandingSettingsFrame, text="Pick Color", command=pickMenuColor, state=DISABLED)
    menuIconColorPicker.grid(row=5, column=1, sticky="e")

    # Branding name color
    brandingNameColorLabel = Label(brandingSettingsFrame, text="Branding Name Color")
    brandingNameColorLabel.grid(row=6, column=0, sticky="w")

    brandingNameColorEntry = Entry(brandingSettingsFrame, textvariable=currentBranding.nameColor, state=DISABLED)
    brandingNameColorEntry.grid(row=7, column=0, sticky="we")

    brandingNameColorPicker = Button(brandingSettingsFrame, text="Pick Color", command=pickNameColor, state=DISABLED)
    brandingNameColorPicker.grid(row=7, column=1, sticky="e")

    # Status bar text color
    statusBarLabelFrame = LabelFrame(brandingSettingsFrame, text="Status Bar Text Color")
    statusBarLabelFrame.columnconfigure(0, weight=1)
    statusBarLabelFrame.columnconfigure(2, weight=1)
    statusBarLabelFrame.columnconfigure(4, weight=1)
    statusBarLabelFrame.grid(row=8, column=0, columnspan=2, sticky="we")

    lightRadioButton = Radiobutton(statusBarLabelFrame, text="Light", variable=currentBranding.statusBarColor, value="light", state=DISABLED, pady=5)
    lightRadioButton.grid(row=0, column=1, sticky="w")

    darkRadioButton = Radiobutton(statusBarLabelFrame, text="Dark", variable=currentBranding.statusBarColor, value="dark", state=DISABLED, pady=5)
    darkRadioButton.grid(row=0, column=3, sticky="e")

    submitAndLoggingFrame = Frame(root, padx=10, pady=10)
    submitAndLoggingFrame.pack(fill=BOTH, expand=True)
    submitAndLoggingFrame.columnconfigure(0, weight=1)

    # Submit button
    submitButton = Button(submitAndLoggingFrame, text="Submit", state=DISABLED, command=putBrandingSettings)
    submitButton.grid(row=0, column=0, sticky="we")

    # Log console
    loggingField = Text(submitAndLoggingFrame, state=DISABLED, wrap=WORD, height=5, borderwidth=1, relief=GROOVE, takefocus=False)
    loggingField.grid(row=1, column=0, pady=10)

    root.mainloop()
