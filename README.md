# FacebookWebBot
(Forked From hikuAi @github)

=======================

A simple library to automatize facebook without the official API
All the functions are made scrapping and parsing mbasic.facebook.com in the english language 

## Available functions:

    Login (100% Working)
    Logout  (100% Working)
	Post in your timeline - Not Working
	Message friends - Not Working
	Get post in a facebook group
	Post in a facebook group - Not Working
	Comment in a post  (100% Working)
	Get the members of a facebook group - Not Working
	Send friend request  (100% Working)
	Send message to any person - Not Working
	Get all post from a profile/fanpage - Not Working
	Send group request - Not Working
	Get number of likes and coments in a post  - (100% Working)
	Post in a fanpage/friend timeline - Not Working
    
## Basic usage example:

```
from FacebookWebBot import *
bot=FacebookBot()
bot.set_page_load_timeout(10)
bot.login("your@email.com","yourpassword")
allpost=bot.GetMyTimeline()
for p in allpost:
	print(p.handle()) #Post Page handle ID
```
## Installing
pip install FacebookWebBot
## Know issues:

    * Can't post images because PhantomJS limitations.

## Dependencies:

    * Python 3.8

    * Selenium

    * Chrome Browser Installed with Webdrivers (https://chromedriver.chromium.org/downloads)
