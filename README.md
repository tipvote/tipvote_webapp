

![alt text](https://www.tipvote.com/images/social_logo_dark.png)


 	
Tipvote.com is a social media site powered by the blockchain.  We enable ways to support content through CryptoCurrency.
 	
 	
## Features

- Support posts or comments in Bitcoin, Bitcoin Cash, Monero, and more to come!
- Create communities or post to your favorite topics.
- Community owners earn a percent of all tips in there communities they manage.
- Limited moderation to support free speech.
- Post boosters to promote posts earned by just using the site.

## Why Tipvote

Everyone wants to have there voice heard and we have multiple ways to do so. 
 We limit moderation to ensure freedom of speech.  

Get tipped for content and be supported by the crypto community.


You can promote a post with very little crypto, to get it to the front of the page. 

When you use the site you get free tipvote coins. 

- These are not crypto/monetary based but apply points (upvotes) to your post.  
- You can earn these coins by posting or commenting.  
- Can not be bought or sold.

## Easy to join and start posting

We don't require any info except an email address.  Takes a few seconds to sign up and you dont need to confirm your email.  


## Installation

Docker will need to be done in a future update. For now manual installation. 
Tested and running on ubuntu 18.04, 20.04, and windows ubuntu
```
sudo apt-get update 

git pull https://github.com/tipvote/tipvote_webapp.git

sudo pip3 install virtualenv
source virtualenv venv -p python3
pip3 install -r requirements.txt

```
Set up a postgres database locally
```
sudo apt-get install postgresql postgresql-contrib
```
Next create a database named avengers with several schemas
```
database name =  avengers
schemas = avengers_admin, avengers_coins, avengers_comments, 
avengers_main, avengers_msg, avengers_post, avengers_promotion, avengers_subforum,
avengers_tips, avengers_user, avengers_user_business, avengers_wallet_bch,
avengers_wallet_bch_test, avengers_wallet_btc, avengers_wallet_btc_test,
avengers_wallet_monero,avengers_wallet_monero_stagenet, avengers_wallet_monero_testnet
```
Comment out the live connection to config file to point to a local connection

run the app (may need to run twice to create mappers)
```
python3 runLan.py
```

Please note:
Other micro apps such as wallets are not needed for running locally.
Images are attached through a nfs mount.  You can create your own mount point
and change this in the config.py file.

```
UPLOADED_FILES_DEST = '/nfs'
```




## Contributing

We are actively looking for members to make this site better.

## License
https://github.com/tipvote/tipvote_webapp/blob/master/license.txt