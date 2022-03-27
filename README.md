# Tweets For Sats

This web app allows users to tweet anonymously for a small stake of 100 sats. 

## Rationale
This web app was created to allow people to tweet without having to sign up for Twitter or sign into their main Twitter account. The user must stake 100 sats for each tweet made. The stake can be reclaimed after 24 hours.

### Why the stake?
The stake exists to discourage spam and bad behavior by charging a small amount of Bitcoin for each tweet. Users can potentially still misbehave but it is limited by the amount of funds they are willing to spend. If a tweet is determined to be spam, the user will lose their stake. Otherwise, the stake can be reclaimed after a waiting period.

### Why Bitcoin and the Lightning network?
Bitcoin is used because its permissionless and requires no identification. The lightning network is used due to its ability to instantly settle low fee microtransactions. No one will want to wait 10 minutes just to make an anonymous tweet. Lightilng is also more private than using onchain transactions.

### Will you moderate content?
Yes. Content that is considered spam will be removed and the user will lose their stake for that tweet.