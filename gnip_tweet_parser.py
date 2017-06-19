import datetime
import sys
try:
    import ujson as json
    json_decode_error = ValueError
except ImportError:
    import json
    if sys.version_info[0] == 3:
        json_decode_error = json.JSONDecodeError
    else:
        json_decode_error = ValueError

from cached_property import cached_property
from tweet_methods.tweet_parser_errors import InvalidJSONError, NotATweetError, NotAvailableError
from tweet_methods import tweet_checking, tweet_date, tweet_user, tweet_text, tweet_geo, tweet_links, tweet_entities, tweet_embeds

class tweet(dict):
    """
    tweet class 
    """
    def __init__(self, json_text = None, tweet_dict = None):
        """
        load the JSON formatted text once and store it as a dictionary
        """
        # potentially deal with character encoding issues?
        # TBD
        if json_text is not None:
            # store the original text
            self.original_json = json_text
            # load & store the Tweet as a dict
            try:
                _tweet_dict = json.loads(json_text)
            except json_decode_error:
                raise InvalidJSONError("Unable to load JSON text")
        elif tweet_dict is not None:
            _tweet_dict = tweet_dict
        else:
            raise(NotATweetError("You didn't even pass me anything."))

        # get the format of the Tweet data--we'll want this for pretty much everything later
        # also, this throws an error if it's not a tweet
        self.original_format = tweet_checking.check_tweet(_tweet_dict)

        # make sure that this obj has all of the keys that our dict had
        self.update(_tweet_dict)
    
    @cached_property
    def id(self):
        """
        return the Tweet id as a string
        """
        if tweet_checking.is_original_format(self):
            return self["id_str"]
        else:
            return self["id"].split(":")[-1]

    @cached_property
    def created_at_seconds(self):
        """
        return seconds since the unix epoch of the Tweet create
        """
        return tweet_date.snowflake2utc(self.id)

    @cached_property
    def created_at_datetime(self):
        """
        return a python datetime obj of the Tweet create
        """
        return datetime.datetime.utcfromtimestamp(self.created_at_seconds)

    @cached_property
    def created_at_string(self):
        """
        return a date string, formatted as: YYYY-MM-ddTHH:MM:SS.000Z
        """
        return self.created_at_datetime.strftime("%Y-%M-%dT%H:%M:%S.000Z")

    @cached_property
    def user_id(self):
        """
        get the user id, as a string
        """
        return tweet_user.get_user_id(self)

    @cached_property
    def screen_name(self):
        """
        get the user screen name (@ handle)
        """
        return tweet_user.get_screen_name(self)

    @cached_property
    def name(self):
        """
        get the user's display name
        """
        return tweet_user.get_name(self)

    @cached_property
    def text(self):
        """
        literally the contents of 'text' or 'body'
        """
        return tweet_text.get_text(self)      

    @cached_property
    def tweet_type(self):
        """
        3 options: tweet, quote, and retweet
        """
        return tweet_text.get_tweet_type(self)

    @cached_property
    def user_entered_text(self):
        """
        text that the actor actually entered 
        not the text of a quote-tweet or the text of a retweet
        all of the text 
        (not truncated, includes @ mention relpies and long links)
        """
        if self.tweet_type == "retweet":
            return ""
        return tweet_text.get_full_text(self)

    @cached_property
    def poll_options(self):
        """
        text in the options of a poll, as a list
        """
        return tweet_text.get_poll_options(self)

    @cached_property
    def quote_or_rt_text(self):
        """
        the text of a quote tweet or a retweet
        """
        return tweet_text.get_quote_or_rt_text(self)        

    @cached_property
    def all_text(self):
        """
        all of the text of the tweet
        Includes @ mentions, long links, quote-tweet contents
        (separated by a newline), RT contents & poll options
        """
        return tweet_text.get_all_text(self)

    @cached_property
    def user_entered_text_without_links(self):
        """
        same as user_entered_text, but links are removed
        """
        return tweet_text.remove_links(self.user_entered_text)

    @cached_property
    def all_text_without_links(self):
        """
        same as all_text, but links are removed
        """
        return tweet_text.remove_links(self.all_text)

    @cached_property
    def geo_coordinates(self):
        """ 
        return the geo coordinates, if they are included in the payload
        else raise 'unavailable field' error
        """
        return tweet_geo.get_geo_coordinates(self)

    @cached_property
    def profile_location_enrichment(self):
        """
        return location data from the profile location profile location enrichment 
        """
        raise NotImplementedError("Sorry!") 

    @cached_property
    def normalized_url_info(self):
        """
        if unrolled urls are availble, return unrolled urls
        if unrolled urls are not availble, return whatever link is availble in entities
        if there are no links, return an empty list
        """
        return tweet_links.get_tweet_links(self)

    @cached_property
    def most_unrolled_urls(self):
        """
        return the most unrolled url present
        """
        return tweet_links.get_most_unrolled_url(self.normalized_url_info)     

    @cached_property
    def user_mentions(self):
        """
        get a list of @ mention dicts from the tweet
        """
        return tweet_entities.get_user_mentions(self)

    @cached_property
    def user_mentions_ids(self):
        """
        get a list of @ mentions user ids from the tweet
        """
        return [x["id_str"] for x in tweet.user_mentions]

    @cached_property
    def mentions_screen_names(self):
        """
        get a list of @ mentions screen names from the tweet
        """
        return [x["screen_name"] for x in tweet.user_mentions]

    @cached_property
    def quoted_user(self):
        """
        quoted users don't get included in the @ mentions 
        which doesn't seem that intuitive, so I'm adding a getter to add them
        """ 
        return tweet_entities.get_quoted_user(self)

    @cached_property
    def quoted_mentions(self):
        """
        users mentioned in the quoted Tweet don't get included 
        which doesn't seem that intuitive, so I'm adding a getter to add them
        """ 
        return tweet_entities.get_quoted_mentions(self)

    @cached_property
    def hashtags(self):
        """
        get a list of hashtags
        """
        return tweet_entities.get_hashtags(self)

    @cached_property
    def quote_tweet(self):
        """
        get the quote tweet and returna  tweet obj of the quote tweet
        """
        return tweet(tweet_dict = tweet_embeds.get_quote_tweet(self))

    @cached_property
    def retweet(self):
        """
        get the retweet and return a tweet obj of the retweet 
        """
        return tweet(tweet_dict = tweet_embeds.get_retweet(self))

    @cached_property
    def embedded_tweet(self):
        """
        get the quote tweet or the retweet and return a tweet object of it
        """
        return tweet(tweet_dict = tweet_embeds.get_embedded_tweet(self))


if __name__ == "__main__":
    # parse arguements
    import argparse
    import fileinput
    import sys
    list_of_attrs = sorted([x for x in list(set(dir(tweet)) - set(dir(dict))) if x[0] != "_"])
    parser = argparse.ArgumentParser(
            description="Parse seqeunce of JSON formated activities.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f","--file", dest="data_files"
        , default="-"
        , help="Name of the file to read from, defaults to stdin")
    parser.add_argument("-c","--csv", dest="func_list"
        , default="id"
        , help="comma separated list of attibutes to get \n possible functions include: \n -> {}".format(" \n -> ".join(list_of_attrs)))
    parser.add_argument("-d","--delim", dest="delim"
        , default="|"
        , help="delimiter for the output csv, defaults to pipe")
    parser.add_argument("-z","--compressed", action="store_true", dest="compressed"
        , default=False
        , help="use this flag if data is compressed")
    options = parser.parse_args()

    # get the functions that we need to use:
    functions = options.func_list.split(",")

    # get the compression
    if options.compressed:
        openhook = fileinput.hook_compressed
    else:
        openhook = None

    # parse some tweets
    for line in fileinput.FileInput(options.data_files, openhook=openhook):
        csv = []
        try:
            tweet_obj = tweet(line)
        except (NotATweetError,JSONDecodeError):
            pass
        for func in functions:
            attribute = getattr(tweet_obj,func)
            if type(attribute)==str:
                attribute = attribute.replace(options.delim," ").replace("\n", " ").replace("\r", " ")
            csv.append(str(attribute))
        sys.stdout.write(options.delim.join(csv) + "\n")




