import GetOldTweets3 as got

tweetCriteria = got.manager.TweetCriteria().setUsername("LTAtrafficnews")\
                                           .setSince("2020-06-05")\
                                           .setUntil("2020-06-08")\
                                           .setEmoji("unicode")
tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]
print(tweet.text)


# GetOldTweets3 --username "LTAtrafficnews" --since 2020-06-05 --until 2020-06-07 --maxtweets 350 --output test.csv
# GetOldTweets3 --username "LTAtrafficnews" --since 2019-04-01 --until 2019-05-01 --maxtweets 1600 --output april.csv #1378
# GetOldTweets3 --username "LTAtrafficnews" --since 2019-05-01 --until 2019-06-01 --maxtweets 1600 --output may.csv #1523
