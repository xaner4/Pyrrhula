# Pyrrhula

A Slack bot for getting keyword tweets from spesified users

it will check the user every 2 minuttes and will check 10 tweets at the time 


## Prerequesite

* Docker
* Docker-Compose
* Twitter bearer token (https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens)
* Slack token (https://api.slack.com/tutorials/tracks/getting-a-token)

## Installation guide

1. Build docker image
```bash
sudo docker compose build
```

2. Configure application
```yaml
twitter:
  bearer_token: "TWITTER_TOKEN"
  users:
    - "elonmusk"
  keywords:
    - "doge"
    - "tesla"
    - "spacex"

slack:
  token: "SLACK_TOKEN"
  channel: "musttweets"
```

3. Start docker container
```bash
sudo docker compose up -d
```


