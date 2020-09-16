from webpreview import web_preview
from validator_collection import validators, checkers

ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp']


def geturl(stringsubmitted):
    headers = {'User-Agent': 'Mozilla/5.0'}
    splits = stringsubmitted.split()
    value = ''
    urltitle = ''
    urldescription = ''
    urlimage = ''

    for f in splits:
        try:
            if len(f) > 5:
                if f.endswith(('.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp')):
                    pass
                else:
                    if not f.lower().startswith(("http://", "https://")):
                        f = 'https://' + f

                    value = validators.url(f)
                    mainurl = (checkers.is_url(value))
                    if mainurl is True:
                        urltitle, urldescription, urlimage = web_preview(value, headers=headers)
                        break
                    else:
                        value = ''
                        urltitle = ''
                        urldescription = ''
                        urlimage = ''
        except:
            pass

    if value is None:
        value = ''
    if urltitle is None:
        urltitle = ''
    if urldescription is None:
        urldescription = ''
    if urlimage is None:
        urlimage = ''

    return value, urltitle, urldescription, urlimage