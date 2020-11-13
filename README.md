

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

Via docker

pull from git
```
git pull https://github.com/tipvote/tipvote_webapp.git
```

Create the Docker image
```
 docker build --tag tipvote:1.0 .
```

Deploy the server 
```
docker run --publish 5000:5000 -d --name tip tipvote:1.0
```

Stop the server 
```
docker rm --force tip
```

then visit your browser and the address is 
```
localhost:5000
```


## Contributing

We are actively looking for members to make this site better.

## License
https://github.com/tipvote/tipvote_webapp/blob/master/license.txt