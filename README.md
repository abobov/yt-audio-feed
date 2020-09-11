# YouTube audio RSS feed

Creates feed with audio from your YouTube subscriptions.

## Usage

To create a simple list:

`$ python3 main.py path-to-opml.xml`

For more options run:

`$ python3 main.py --help`

## Get OPML for you subscriptions

Look for *Get RSS updates for all subscriptions* in [Use RSS with YouTube](https://support.google.com/youtube/answer/6224202)

## Docker

Build image with:

`$ docker build --tag yt-audio-feed .`

And run it:

`$ docker run -it -v $PWD:/data yt-audio-feed /data/subscription_manager.xml -o /data/output.xml`
