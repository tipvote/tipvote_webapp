

def transform_image_links_markdown(stringsubmitted):
    from app import db
    from app.models import User
    from sqlalchemy import func
    splits = stringsubmitted.split()
    worktobedone = []

    extra_name = None

    for f in splits:

        # see if images url
        try:
            if f.endswith(('.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp')):
                if f.lower().startswith(("http://", "https://")):
                    newstring = '![alt text](' + f + ')'
                    theword = f

                    worktobedone.append(theword)
                    worktobedone.append(newstring)

            # see if username mentions
            elif f.startswith('/u/'):
                if 3 <= len(f) <= 25:
                    newname = f[3:]
                    newname = newname.lower()

                    # see if user exists
                    get_user = db.session.query(User).filter(func.lower(User.user_name) == newname).first()
                    if get_user:
                        theurl = "["+f+"](https://www.tipvote.com/u/" + newname + ")"

                        newstring = theurl
                        theword = f

                        worktobedone.append(theword)
                        worktobedone.append(newstring)

                        extra_name = get_user
                    else:
                        pass
                else:
                    pass
            # see if room name mentions
            elif f.startswith('/a/'):
                if 3 <= len(f) <= 50:
                    newname = f[3:]
                    theurl = "[" + f + "](https://www.tipvote.com/a/" + newname + ")"

                    newstring = theurl
                    theword = f

                    worktobedone.append(theword)
                    worktobedone.append(newstring)

                else:
                    pass
            else:
                pass
        except:

            extra_name = None
    if not worktobedone:
        newstring = stringsubmitted
    else:
        newstring = stringsubmitted.replace(worktobedone[0], worktobedone[1])
    extra_name = extra_name

    return newstring, extra_name


