import matplotlib.pyplot as plt
import redditComments as rc
# Example
if __name__ == "__main__":
    subreddits = [rc.redditComments("AskReddit", 10, 365,10000),\
                  rc.redditComments("askscience", 10, 365,10000),\
                  rc.redditComments("jokes", 10, 365,10000)]

    plt.figure(figsize=(10,5))
    for i in subreddits:
        plt.scatter(i.upvotes,i.commentLength, label="r/" + i.subreddit, linewidth=0.5)
    plt.legend()
    plt.xlabel("Fraction Post to Comment upvotes / %")
    plt.ylabel("Comment length / words")
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.savefig("results.png", dpi=150, bbox_inches="tight")
    plt.close()
