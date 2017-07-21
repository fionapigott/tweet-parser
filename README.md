# gnip-tweet-parser
Authors: Fiona Pigott, Jeff Kolb

## Goal:
Allow reliable parsing of Tweets delivered by the Gnip platform, in both activity-streams and original formats. 

## Status:
This package is not yet available on pypi, but soon it should be. For now, recommended usage would be to clone the repository and `pip install -e .` Only Python 3 is supported.

## Usage:
This package is intended to be used as a Python module inside your other Tweet-related code. An example Python program (after pip installing the package) would be:

```
from tweeet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
import fileinput
import ujson

for line in fileinput.FileInput("gnip_tweet_data.json"):
    try:
        tweet_dict = ujson.loads(line)
        tweet = Tweet(tweet_dict)
    except (ValueError,NotATweetError):
        pass
    print(tweet.created_at_string, tweet.all_text)
```

I've also added simple command-line utility:

```
python tools/tweet_parser.py -f"gnip_tweet_data.json" -c"created_at_string,all_text"
```
## Testing:
A Python `test_tweet_parser.py` package exists in `test/`. 

The most important thing that it tests is the equivalence of outputs when comparing both activity-streams input and original-format input. Any new getter will be tested by running `test$ python test_tweet_parser.py`, as the test checks every method attached to the Tweet object, for every test tweet stored in `test/tweet_payload_examples`. For any cases where it is expected that the outputs are different (e.g., outputs that depend on poll options), conditional statements should be added to this test.

An option also exists for run-time checking of Tweet payload formats. This compares the set of all Tweet field keys to a superset of all possible keys, as well as a minimum set of all required keys, to make sure that each newly loaded Tweet fits those parameters. This shouldn't be run every time you load Tweets (for one, it's slow), but is implemented to use as a periodic check against Tweet format changes. This option is enabled with `--do_format_checking` on the command line, and by setting the keyword argument `do_format_checking` to `True` when initializing a `Tweet` object.
