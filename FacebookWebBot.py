# coding: utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import re
from datetime import *

selfProfile = "https://mbasic.facebook.com/profile.php?fref=pb"


def mfacebookToBasic(url):
    """Reformat a url to load mbasic facebook instead of regular facebook, return the same string if
    the url don't contains facebook"""

    if "m.facebook.com" in url:
        return url.replace("m.facebook.com", "mbasic.facebook.com")
    elif "www.facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com")
    else:
        return url


class Person():
    """Basic class for people's profiles"""

    def __init__(self):
        self.name = ""
        self.profileLink = ""
        self.addLink = ""

    def __str__(self):
        s = ""
        s += self.name + ":\n"
        s += "Profile Link: " + self.profileLink
        if self.addLink != "":
            s += "Addlink ->: " + self.addLink
        return s

    def __repr__(self):
        self.__str__()


class post():
    fbData = []

    def __init__(self, data):
        self.fbData = data

    def author(self):
        return str(self.fbData['author'])

    def authorURL(self):
        return str(self.fbData['author_page'])

    def content(self):
        return str(self.fbData['content'])

    def likes(self):
        return int(self.fbData['likes'])

    def comments(self):
        return int(self.fbData['comments'])

    def storyURL(self):
        return self.fbData['post_url'][0] or None

    def handle(self):
        if self.storyURL() is not None:
            handle = re.search("(?!story_fbid=)[0-9]+", str(self.storyURL()))
            return int(handle.group())
        else:
            return 0

    def timestamp(self):
        return int(self.fbData['timestamp'])

    def data(self): #debug Data
        return self.fbData

class Post():
    """Class to contain information about a post"""

    def __init__(self):
        self.posterName = ""
        self.text = ""
        self.numLikes = 0
        self.time = ""
        self.privacy = ""
        self.posterLink = ""
        self.linkToComment = ""
        self.linkToLike = ""
        self.linkToLikers = ""
        self.linkToReport = ""
        self.groupLink = ""
        self.linkToShare = ""
        self.linkToMore = ""
        self.numComents = 0

    def toDict(self):
        return self.__dict__.copy()

    def fromDict(self, d):
        self.__dict__ = d.copy()

    def from_json(self, j):
        self.fromDict(json.loads(j))

    def from_json_file(self, f):
        self.fromDict(json.loads(open(f, "rt").read()))

    def to_json(self):
        return json.dumps(self.toDict())

    def __str__(self):
        s = "\nPost by " + self.posterName + ": "
        s += self.text + "\n"
        s += "Likes: " + str(self.numLikes) + " - "
        s += "Comments: " + str(self.numComents) + " - "
        s += self.time + " "
        s += " - Privacy: " + self.privacy + "\n-"
        s += "\n Comment -> " + self.linkToComment + "\n"
        return s

    def __repr__(self):
        return self.__str__()


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)


class FacebookBot(webdriver.Chrome):
    """Main class for browsing facebook"""

    myname = None

    def __init__(self, executable_path, Name, debug_mode=False):
        self.myname = Name
        # pathToPhantomJs ="
        """relativePhatomJs = "\\phantomjs.exe"
        service_args = None
        if images == False:
            service_args = ['--load-images=no', ]
        if pathToPhantomJs == None:
            path = self, os.getcwd() + relativePhatomJs
        else:
            path = pathToPhantomJs
            webdriver.PhantomJS.__init__(self, path, service_args=service_args)
        """
        options = Options()
        options.headless = debug_mode
        webdriver.Chrome.__init__(self, executable_path, chrome_options=options)

    def get(self, url):
        """The make the driver go to the url but reformat the url if is for facebook page"""
        super().get(mfacebookToBasic(url))
        self.save_screenshot("Debug.png")

    def login(self, email, password):
        """Log to facebook using email (str) and password (str)"""

        url = "https://mbasic.facebook.com"
        self.get(url)
        email_element = self.find_element_by_name("email")
        email_element.send_keys(email)
        pass_element = self.find_element_by_name("pass")
        pass_element.send_keys(password)
        pass_element.send_keys(Keys.ENTER)

        try:
            if self.find_element_by_xpath('//*[@id="objects_container"]/div[1]/h2').is_displayed():
                if "feature at the moment" in self.find_element_by_xpath('//*[@id="objects_container"]/div[1]/h2').text:
                    print("[Error]: We have been Blocked by facebook!")
                    return False
        except NoSuchElementException:
            pass

        if self.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/div/form').is_displayed():
            self.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/div/form/div/input').click()

        try:
            self.find_element_by_name("xc_message")
            print("Logged in")
            return True
        except NoSuchElementException as e:
            print("Fail to login")
            return False

    def logout(self):
        """Log out from Facebook"""

        if self.current_url != "https://mbasic.facebook.com/home.php":
            self.get("https://mbasic.facebook.com/home.php")

        try:
            self.find_element_by_xpath('// *[ @ id = "mbasic_logout_button"]').click()
            return True
        except Exception as e:
            print("Failed to log out ->\n", e)
            return False

    def postTextToURL(self, text, url):
        """Post text(str) to url (str), url can be a group, fan page or profile"""

        try:
            self.get(url)
            textbox = self.find_element_by_name("xc_message")
            textbox.send_keys(text)
            submit = self.find_element_by_name("view_post")
            submit.click()
            return True
        except Exception as e:
            print("Failed to post in ", url, "->\n", e)
            return False

    def postTextToTimeline(self, text):
        """Shortcut to post in your own timeline"""

        url = "https://mbasic.facebook.com/"
        return self.postTextToURL(text, url)

    def newMessageToFriend(
            self,
            friendname,
            message,
            image1=None,
            image2=None,
            image3=None):
        """Send message(str) to friend name (str), images doesn work in phantomjs"""

        url = "https://mbasic.facebook.com/friends/selector/?return_uri=%2Fmessages%2Fcompose%2F&cancel_uri=https%3A%2F%2Fm.facebook.com%2Fmessages%2F&friends_key=ids&context=select_friend_timeline&refid=11"
        self.get(url)
        q = self.find_element_by_name("query")
        q.send_keys(friendname)
        q.send_keys(Keys.ENTER)
        id = self.page_source.split(
            "/messages/compose/?ids=")[1].split('"><span>')[0].split('"><span>')[0]
        url = "https://mbasic.facebook.com/messages/compose/?ids=" + id
        self.get(url)
        t = self.find_element_by_name("body")
        t.send_keys(message)
        t.send_keys(Keys.ENTER)
        f1 = self.find_element_by_name("file1")
        f2 = self.find_element_by_name("file2")
        f3 = self.find_element_by_name("file3")
        if image1 is not None:
            f1.send_keys(image1)
        if image2 is not None:
            f2.send_keys(image2)
        if image3 is not None:
            f3.send_keys(image3)
        send = self.find_element_by_name("Send")
        send.send_keys(Keys.ENTER)
        return True

    def getPostInGroup(self, url, deep=2, moreText="Ver m??s publicaciones"):
        """Get a list of posts (list:Post) in group url(str) iterating deep(int) times in the group
        pass moreText depending of your language, i couldn't find a elegant solution for this"""

        self.get(url)
        ids = [4, 5, 6, 7, 9]
        posts = []
        for n in range(deep):
            #print("Searching, deep ",n)
            for i in ids:
                # print(i)
                post = Post()
                try:
                    p = self.find_element_by_id("u_0_" + str(i))
                    # print(p.text)
                    a = p.find_elements_by_tag_name("a")
                    post.posterName = a[1].text
                    try:
                        post.numLikes = int(a[3].text.split(" ")[0])
                    except ValueError:
                        post.numLikes = 0
                    post.text = p.find_element_by_tag_name("p").text
                    post.time = p.find_element_by_tag_name("abbr").text
                    # p.text.split("?? ")[1].split("\n")[0]
                    post.privacy = self.title
                    post.posterLink = a[0].get_attribute('href')
                    # p.find_element_by_class_name("du").get_attribute('href')
                    post.linkToComment = a[2].get_attribute('href')
                    post.linkToLike = a[4].get_attribute('href')
                    try:
                        post.numComents = int(a[5].text.split(" ")[0])
                    except ValueError:
                        post.numComents = 0
                    # post.linkToShare = a[5].get_attribute('href')
                    post.linkToLikers = a[1].get_attribute('href')
                    post.linkToMore = a[6].get_attribute('href')
                    if post not in posts:
                        posts.append(post)
                except Exception:
                    continue
            try:
                more = self.find_element_by_partial_link_text(
                    moreText).get_attribute('href')
                self.get(more)
            # self.find_element_by_partial_link_text(moreText)
            except Exception as e:
                print(e)
                print(" Can't get more posts")
        return posts

    def postInGroup(self, groupURL, text):
        """Post text(str) in a group"""

        self.get(groupURL)
        try:
            tf = self.find_element_by_name("xc_message")
        except NoSuchElementException:
            print(" Group url doesn't exist or you don't have permissions to see it")
            return False
        tf.send_keys(text)
        self.find_element_by_name("view_post").send_keys(Keys.ENTER)
        return True

    def like(self, URL):
        print("Liking Post")
        if self.current_url != URL:
            self.get(URL)

        storyID = re.search("(?!story_fbid=)[0-9]+", str(self.current_url))

        result = self.find_element_by_xpath('//*[@id="actions_{}"]/table/tbody/tr/td[1]/a'.format(storyID.group())).get_attribute("aria-pressed")

        if result == "false":
            self.find_element_by_xpath('//*[@id="actions_{}"]/table/tbody/tr/td[1]/a'.format(storyID.group())).click()
            result = self.find_element_by_xpath('//*[@id="actions_{}"]/table/tbody/tr/td[1]/a'.format(storyID.group())).get_attribute("aria-pressed")
            if result == "true":
                return True
        else:
            print("Already Liked")
            return False

    def comment(self, URL, text):
        print("Posting a comment..")
        if self.current_url != URL:
            self.get(URL)
        ele = self.find_element_by_xpath('//*[@id="composerInput"]')
        ele.send_keys(text)
        self.implicitly_wait(1)
        ele.submit()
        return True

    def GetMyTimeline(self):

        if (self.current_url != "https://mbasic.facebook.com/home.php"):
            self.get('https://mbasic.facebook.com/home.php')

        print("Getting Post in timeline..")
        posts = []

        articles = self.find_elements_by_tag_name("article")
        print("Found {} Public Posts.".format(len(articles)))

        for article in articles:
            footer_data = None
            body_data = None

            footer = article.find_elements_by_tag_name("footer")
            header = article.find_elements_by_tag_name("header")
            body = article.find_elements_by_class_name('dx')

            if (len(body) > 0):
                body_data = body[0].text

            if (len(footer) > 0):
                footer_data = footer[0].text


            profile_URL = header[0].find_elements_by_tag_name('a')[0].get_attribute("href") or None

            Footer_urls = []
            for url in footer[0].find_elements_by_tag_name('a'):
                if "story.php" in url.get_attribute("href"):
                    Footer_urls.append(url.get_attribute("href"))

            fdata = self.Footer_fit(footer_data)
            DataList = {
                        **{"author": header[0].text},
                        **{"author_page": profile_URL},
                        **{"content": body_data},
                        **fdata,
                        **{"post_url": Footer_urls or None}
                        }

            posts.append(post(DataList))

        return posts


    def postImageInGroup(self, url, text, image1, image2="", image3=""):
        """Post image(str) in a group(url:str) with the text(str), doesn't work in phantomJS"""
        self.get(url)
        v = self.find_element_by_name("view_photo")
        v.send_keys(Keys.ENTER)
        self.save_screenshot("debug.jpg")
        i1 = self.find_element_by_name("file1")
        i2 = self.find_element_by_name("file2")
        i3 = self.find_element_by_name("file3")
        i1.send_keys(image1)
        i2.send_keys(image2)
        i3.send_keys(image3)
        filter = self.find_element_by_name("filter_type")
        filter.value_of_css_property(0)
        pre = self.find_element_by_name("add_photo_done")
        pre.click()
        m = self.find_element_by_name("xc_message")
        m.send_keys(text)
        vp = self.find_element_by_name("view_post")
        vp.click()
        return True

    def commentInPost(self, postUrl, text):
        """Comment a text(str) in a post(str)"""
        try:
            self.get(postUrl)
            tb = self.find_element_by_name("comment_text")
            tb.send_keys(text)
            tb.send_keys(Keys.ENTER)
            return self.getScrenshotName("CommentingIn_" + self.title, screenshot, screenshotPath)
        except Exception as e:
            print("Can't comment in ", postUrl, "\n->", e)

    def getGroupMembers(self, url, deep=3, start=0):
        """Return a list of members of a group(url) as a list:Person iterat deep(int) times"""

        seeMembersUrl = url + "?view=members&amp;refid=18"
        groupId = url.split("groups/")[1]
        step = 28
        r = "https://mbasic.facebook.com/browse/group/members/?id=$GROUPID$&start=$n$"
        rg = r.replace("$GROUPID$", groupId)
        members = []
        for d in range(start, start + deep):
            url = rg.replace("$n$", str(d * 30))
            self.get(url)
            # print(self.current_url)
            p = self.find_elements_by_class_name("p")  # BK cada profile
            for b in p:
                person = Person()
                h3 = b.find_elements_by_tag_name("h3")
                person.name = h3[0].text
                person.profileLink = h3[0].find_element_by_tag_name(
                    "a").get_attribute('href')
                try:
                    person.addLink = b.find_elements_by_tag_name(
                        "a")[1].get_attribute('href')  # puede haber error
                except Exception:
                    # print("No Addlink")
                    pass
                members.append(person)
                # more = self.find_element_by_id("m_more_item").find_element_by_tag_name("a").get_attribute('href')
                # self.get(more)
                # print(more)
        # print(len(members))
        return members


    def sendFriendRequest(self, url):
        """Send a friend request to a profile(str)"""
        if self.current_url != url:
            self.get(url)

        target_name = self.find_element_by_xpath('//*[@id="root"]/div[1]/div[1]/div[2]/div/span/div/span/strong').text
        print("Sending Friend Request to {}".format(target_name))

        try:
            self.find_element_by_xpath('//*[@id="root"]/div[1]/div[1]/div[3]/table/tbody/tr/td[1]/a').click()
            if(self.find_element_by_xpath('//*[@id="root"]/div[1]/div[1]/div[1]/div[1]/div/table/tbody/tr/td[1]/input').is_displayed()):
                print("Friend Request Sent!")
                return True
            else:
                print("Friend Request was not sent!")
                return False
        except Exception:
                print("Can't add friend")
                return False

    def messageToUrl(self, url, text):
        """Message a profile/fanpage (str) with text(str)"""

        self.get(url)
        name = self.title
        try:
            mb = self.find_elements_by_class_name("bx")
        except NoSuchElementException:
            print("Can't message to ", name)
            return False
        mm = None
        for m in mb:
            if "messages" in m.get_attribute('href'):
                mm = m.get_attribute('href')
                break
        self.get(mm)
        b = self.find_element_by_name("body")
        b.send_keys(text)
        self.find_element_by_name("Send").click()
        return True

    def getGroups(self):
        """
        Return a list of url of the groups your account belong to"""
        url = "https://m.facebook.com/groups/?seemore"
        # g = {"name": ("url", 0)}
        g = dict()
        self.get(url)
        br = self.find_elements_by_class_name("br")
        for b in br:
            try:
                notis = int(b.text[-2:])
                group_name = b.text[:-2]
            except ValueError:
                group_name = b.text
                notis = 0
            try:
                link = b.find_element_by_tag_name("a").get_attribute('href')
                g[group_name] = (mfacebookToBasic(link), notis)
            except Exception as e:
                print("Can't get group link")
        return g

    def getSuggestedGroups(self, sendrequest=False):
        """
        Return a list of suggested groups and optionally send a request to join"""

        url = "https://m.facebook.com/groups/"
        g = dict()
        self.get(url)
        bq = self.find_elements_by_class_name("bq")[-1]
        li = bq.find_elements_by_tag_name("li")
        for l in li:
            nombre = l.find_elements_by_tag_name(
                "td")[0].find_elements_by_tag_name("a")[0].text
            description = l.find_elements_by_tag_name(
                "td")[0].find_elements_by_class_name("bx")[0].text
            linkToGroup = l.find_elements_by_tag_name(
                "td")[0].find_element_by_tag_name("a").get_attribute('href')
            linkToRequest = l.find_elements_by_tag_name(
                "td")[-1].find_element_by_tag_name("a").get_attribute('href')
            g[nombre] = (description, linkToGroup, linkToRequest)
        if sendrequest:
            for r in g:
                try:
                    self.get(g[r][2])
                    print("Request to group: ", r)
                except Exception:
                    print("Fail to send request to: ", r)
        return g

    def getPostInTimeline(self, profileURL=None):
        print("Getting Post in timeline..")
        posts = []

        if profileURL is not None:
            self.get(profileURL)
        articles = self.find_elements_by_tag_name("article")
        print("Found {} Public Posts.".format(len(articles)))

        for article in articles:
            footer_data = None
            body_data = None
            urls = None

            footer = article.find_elements_by_tag_name("footer")
            header = article.find_elements_by_tag_name("header")
            body = article.find_elements_by_class_name('_5rgn')

            if (len(body) > 0):
                body_data = body[0].text

            if (len(footer) > 0):
                footer_data = footer[0].text
                urls = footer[0].find_elements_by_tag_name('a')
                #print(footer_data)

            print(urls)

            fdata = self.Footer_fit(footer_data)
            DataList = {**{"title": header[0].text}, **{"content": body_data}, **fdata, **{"URLS": urls}}

            posts.append([DataList])

        return posts

    def Footer_fit(self, data):
        def enum_month(string):
            string = string.lower()
            return {
                'january': 1,
                'february': 2,
                'march': 3,
                'april': 4,
                'may': 5,
                'june': 6,
                'july': 7,
                'august': 8,
                'september': 9,
                'october': 10,
                'november': 11,
                'december': 12
            }[string]

        postdate = re.search("^([0-9]+ [A-z]+ [0-9]+ at [0-9]+:[0-9]+)", str(data))
        comments = re.search("([0-9]+ Comments)", str(data))
        likes = re.search("([0-9]+ ?? Like)", str(data))

        if comments != None:
            comments = comments.group().replace(" Comments", "")
        else:
            comments = 0

        if likes != None:
            likes = likes.group().replace(" ?? Like", "")
        else:
            likes = 0
        if "at" in data:
            if postdate != None:
                date = postdate.group().replace("at ", "").split()
                dt = datetime(int(date[2]), int(enum_month(date[1])), int(date[0]))
                timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
            else:
                timestamp = 0

        if "hrs" in data:
            postdate = re.search("^([0-9]+ hrs)", str(data))
            if postdate != None:
                gethours = int(postdate.group().replace(" hrs", ""))
                timestamp = datetime.now().timestamp() - (100*60*gethours)
            else:
                timestamp = 0

        return {"timestamp": timestamp, "likes": likes, "comments": int(comments)}


    def getPostInProfile(
        self,
        profileURL,
        deep=100,
        moreText="Mostrar",
        sharedText=(
            "shared",
            "comparti",
            "compartio")):
        """Return a list of Posts in a profile/fanpage , setup the "moreText" using your language, theres not elegant way to handle that"""
        pList = list()
        self.get(profileURL)
        # DEEP1
        n = 0
        for d in range(deep):
            try:
                for i in (3, 4, 5, 6, 7):
                    try:
                        e = self.find_element_by_id("u_0_" + str(i))
                        tU = str(e.text)
                    except Exception:
                        continue
                    try:
                        tspl = tU.split(self.title)[1].split("\n")[:-3]
                    except IndexError:
                        continue
                    tFi = ""
                    for k in tspl:
                        tFi += k
                    if sharedText[0] in tFi or sharedText[1] in tFi or sharedText[2] in tFi:
                        continue
                    if tFi not in pList:
                        pList.append(tFi)
                        n += 1
                        print(n, "-\n", tFi)
                    else:
                        continue
                # press more

                al = self.find_element_by_partial_link_text(moreText)
                link = al.get_attribute('href')
                self.get(link)
            except BaseException:
                pass
        return pList

    def getAlbums(self, profileURL):
        self.get(profileURL+"/photos/?refid=17")
        more= self.find_element_by_class_name("cb")
        self.get(more.find_element_by_tag_name("a").get_attribute('href'))
        a= self.find_elements_by_class_name("t")
        alb=dict()
        for aa in a:
            alb[aa.text]=aa.find_element_by_tag_name("a").get_attribute('href')
            #print(alb)
        return alb

    def getPhotosFromAlbum(self,albumURL,direction=1, deep=20):# direction 1= next, -1= previus
        self.get(albumURL)
        first = self.find_element_by_id("thumbnail_area")
        self.get(first.find_element_by_tag_name("a").get_attribute('href'))
        imagesURL = list()
        tags=["bz","by","ca"]
        truenames = list()
        for n in range(deep):
            print(self.title," - photo...",n+1)
        try:
            for t in tags:
                imageurl = self.find_elements_by_class_name(t)[0].get_attribute('href')
                if imageurl != None:
                    #print(imageurl)
                    break
        except:
            print(self.current_url)
            return

        truename = imageurl.split("?")[0].split("/")[-1]

        if truename in truenames:
            print("Repeated...")

        truenames.append(truename)

        imagesURL.append(imageurl)
        td = self.find_elements_by_tag_name("td")
        previusURL = td[0].find_element_by_tag_name("a").get_attribute('href')
        nextURL = td[1].find_element_by_tag_name("a").get_attribute('href')

        #print(nextURL)
        #print(previusURL)

        if direction==1:
            #print("Next")
            self.get(nextURL)
        elif direction==-1:
            #print("Previous")
            self.get(previusURL)
            #print(n,"-   ",imageurl)
        return imagesURL

