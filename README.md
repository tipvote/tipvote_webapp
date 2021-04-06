

![alt text](https://www.tipvote.com/images/social_logo_dark.png)


 	
Tipvote.com is a social media site powered by the blockchain. 
We enable ways to support content through CryptoCurrency.
 	
 	
## Features

- Support posts or comments in Bitcoin, Bitcoin Cash, Monero, and more to come!
- Create communities or post to your favorite topics.
- Community owners earn a percent of all tips in there communities they manage.
- Limited moderation to support free speech.
- Earn real crypto by using the site.  NO ICO coins ..rather bitcoin/monero/etc..

## Why Tipvote

Everyone wants to have there voice heard and we have multiple ways to do so. 
 We limit moderation to ensure freedom of speech.  

Get tipped for content and be supported by the crypto community.


## Easy to join and start posting

We don't require any info except an email address.  Takes a few seconds to sign 
up and you dont need to confirm your email.  


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
https://github.com/tipvote/tipvote_webapp/blob/master/license.txt# tipvote_frontend
