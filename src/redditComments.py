import json
import requests
import sys
import re


class tools:
    """
    Tools Class

    Attributes
    ----------
    none

    Methods
    -------
    errorExit(err)
        prints Error err and exits program
    removeEdit(inBody)
        Removes edits in comments, since they are not part of the original comment.
    """
    def errorExit(self, err):
        print("ERROR:")
        print(err)
        print("Exiting programm...")
        sys.exit()

    def removeEdit(self, inBody):
        inBody = inBody.split(" ")
        body =[]
        for i in range(len(inBody)):
            if re.search('edit', inBody[i], re.IGNORECASE) == None:
                body.append(inBody[i])
            else:
                break
        body = " ".join(body)
        return body

class redditComments:
    """
    Tools Class

    Attributes
    ----------
    helper : class
        tools object
    limit : int
        Amount of threads to investigate
    days : int
        Age of the oldest thread to investigate in days
    subreddit : str
        Name of subreddit
    apiUrlSubreddit : str
        URL of API call
    data : dict
        Holds all fetched data.
    threadUpvotes : str
        minimal upvotes a thread must have to be considered
    upvotes : list
        All upvotes of comments in one thread in ascending order
    commentLength : list
        Length of comments in same order as upvotes

    Methods
    -------
    getThreads()
        Feteches threads
    getComments()
        Fetches comments of all fetched threads
    structureData()
        Convert data dictionary in two seperate arrays
    """
    def __init__(self, inSubreddit, inLimit,inDays,inThreadUpvotes=50000):
        self.helper = tools()
        try:
            self.limit = int(inLimit)
            self.days = int(inDays)
        except ValueError as te:
            self.helper.errorExit(te)

        self.subreddit = inSubreddit
        self.apiUrlSubreddit = "Not yet defined"
        self.data = {"name": [], "id": [], "upvotes": [], "comments": []}
        self.threadUpvotes = inThreadUpvotes
        self.upvotes = []
        self.commentLength = []
        print("Fetching Threads in {}...".format(inSubreddit    ))
        self.getThreads()
        print("Fetching comments in each thread...")
        self.getComments()
        print("Preparing data...")
        self.structureData()
        print("\n\n")


    def __str__(self):
        out = "Subreddit: " + self.subreddit + "\n"
        out += "apiURL: " + self.apiUrlSubreddit + "\n\n"
        out += "Threads to be examined in subreddit (ID; Upvotes; Name):\n"
        for i in range(len(self.data["name"])):
            out += "**************************\n"
            out += self.data["id"][i] + "; " + str(self.data["upvotes"][i]) + "; "
            name = self.data["name"][i]
            if len(name) > 30:
                out += name[:30] + "...\n"
            else:
                out += name + "\n"
            out += "Comments (upvotes; length of command):\n"
            for j in range(len(self.data["comments"][i])):
                out += str(self.data["comments"][i][j][0]) + "; " + str(self.data["comments"][i][j][1]) + "\n"
            out += "**************************\n\n"
        return out


    def getThreads(self):
        self.apiUrlSubreddit = "https://api.pushshift.io/reddit/submission/search/?subreddit={}&limit={}&after={}d&score=>{}"\
                        .format(self.subreddit, self.limit, self.days, self.threadUpvotes)
        data = requests.get(self.apiUrlSubreddit, headers = {'User-agent': 'CommentSizeCorrelation'})
        getJSON = data.json()

        for i in range(self.limit):
            try:
                self.data["name"].append(getJSON["data"][i]["title"])
                self.data["id"].append( getJSON["data"][i]["id"])
                self.data["upvotes"].append(getJSON["data"][i]["score"])
            except:
                print("Problem. Not enough threads to reach limit of {} threads with {} upvotes at least.".format(self.limit,self.threadUpvotes))
                # When amount of fetched threads is smaller than half of the limit -> exit
                if i < self.limit/2:
                    print("exiting program")
                    sys.exit()
                else:
                    print("Using data of {} fetched threads.".format(i))
                    break


    def getComments(self):
        for i in range(len(self.data["name"])):
            commentLimit = 20
            id = self.data["id"][i]
            apiUrlComments = "https://www.reddit.com/r/{}/comments/{}.json?limit={}&sort=top".format(self.subreddit, id, commentLimit)
            data = requests.get(apiUrlComments, headers = {'User-agent': 'CommentSizeCorrelation'})
            getJSON = data.json()

            j = 0
            tempComments = []
            while True:
                try:
                    ups = getJSON[1]["data"]["children"][j]["data"]["ups"]
                    body = getJSON[1]["data"]["children"][j]["data"]["body"]
                    body = self.helper.removeEdit(body)
                    upsBody = (ups, len(body))
                    tempComments.append(upsBody)
                    j += 1
                except KeyError:
                    break
                except:
                    print(self.data["id"][i])

            self.data["comments"].append(tempComments)

    def structureData(self):
        commentArray = [[0,0]]
        for i in range(len(self.data["name"])):
            threadUpvotes = self.data["upvotes"][i]
            factor = 100 / threadUpvotes
            for j in range(len(self.data["comments"][i])):
                ups = factor * self.data["comments"][i][j][0]
                length = self.data["comments"][i][j][1]
                doubleCheck = False
                # If upvotes already in array, caculate mean with new value
                for k in commentArray:
                    if k[0]==ups:
                        k[1] = (k[1] + length)/2
                        doubleCheck = True
                        break
                if not doubleCheck:
                    commentArray.append([ups,length])
                else:
                    doubleCheck = False

        commentArray.sort(key=lambda el: el[0])

        self.upvotes = [i[0] for i in commentArray]
        self.commentLength = [i[1] for i in commentArray]
