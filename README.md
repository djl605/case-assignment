 # FogBugz Random Case Assignment

Welcome to case assignment!

This project can be used to facilitate random assignment of cases to members of your team on a weighted basis.

# Getting Started

## Create an "Up For Grabs" User

The Up For Grabs User, or UFG, is the user you will assign a case to when you want it to be randomly assigned to a member of your team. To create this user:

1. With an admin account, go to **Admin** (in FogBugz Ocelot, **Gear Icon**) > **Users**
1. Add a user from that page
1. To get the ixPerson value for this user (which you'll need later), click on the "Edit" button next to the user on the user list. The URL of the page you are taken to will end in a number. That number is the ixPerson value.


# Setting Up Shares

Shares represent a portion of cases that a given person will receive. For example, suppose we assign

- 4 shares to Mark
- 5 shares to Sarah
- 2 shares to Sam

Then cases will be randomly assigned to Mark with 4/11 probability, to Sarah with 5/11 probability, and to Sam with 2/11 probability. That is assuming the case is due on a day when everybody is marked as in the office on their FogBugz schedule.

If someone has listed a vacation in their FogBugz working schedule, that person will not be considered for assignment for cases due on that day. If *nobody* is available for case assignment on a certain day, any cases due on that day will not be assigned, and will instead remain assigned to the UFG user. Any case edit triggers another attempt at assignment.

A FogBugz administrator can set up the shares for assignment. To do this, click the "Show Live" button in Glitch to see the share assignment page. You will have to authenticate with a FogBugz token to confirm that you are indeed a FogBugz administrator.

Upon authentication, you will be presented with an "Add User" button. Add all the users who you wish to be assigned cases and delegate shares appropriately. Make sure to save your changes.


# Configure the FogBugz Webhook

You have already told the case assignment app about your FogBugz site. Now you have to tell your FogBugz site about the case assignment app. The way to get to the webhook configuration page differs between FogBugz Ocelot (i.e. On Demand and On Site) and FogBugz For Your Server.

For FogBugz For Your Server (version 8.8.55 and earlier):

- Go to **Admin** > **Plugins**
- Make sure the "URLTrigger" plugin is enabled and click the "Configure" button next to it

For FogBugz Ocelot (later than 8.8.55):

- Go to **Gear icon** > **Webhooks**

Once you are on the webhook configuration page, create a new webhook.

- Select the "Case Events" checkbox. This should cause all of the checkboxes for various types of events on cases to become checked.

- In the URL field, type the following:

> https://case-assignment.glitch.me/hooks?ixBug={CaseNumber}&dueDate={DueDate}&url=**<fogbugz_url>**

> Replace **<fogbugz_url>** with the base URL of your FogBugz account. For example:
> - FogBugz On Demand: `https://example.fogbugz.com`
> - FogBugz On Site: `https://fogbugz.mycompany.com`
> - FogBugz For Your Server: `https://my.company.com/fogbugz`

- Set the Hook Type to "GET"

- Set the Filter field to:

> AssignedToId = **<N>**

> (replace **<N>** with the ixPerson number of your UFG user. The number must be in quotes.)

- You can give the webhook any name you want; "UFG" is a good option.

- Click OK


# That's It!

Case assignment is now configured! Any time you want to change the shares around, you can come back to your project and make the changes the way you did when you originally set them. To have a case randomly assigned, just assign it to the UFG user.

Note that it may take up to a minute for the case to be randomly assigned after assigning to UFG. This is due to the asynchronous nature of FogBugz webhooks, meaning the webhook may not fire until a few moments after the case is edited.


# Support

If you have any questions, feel free to email fogbugz.case.assignment@gmail.com