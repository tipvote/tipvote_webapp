

def transform_image_links_markdown(stringsubmitted):
    splits = stringsubmitted.split()
    worktobedone = []
    for f in splits:
        try:
            if f.endswith(('.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp')):
                if f.lower().startswith(("http://", "https://")):
                    newstring = '![alt text](' + f + ')'
                    theword = f

                    worktobedone.append(theword)
                    worktobedone.append(newstring)
                else:
                    pass
            else:
                pass
        except:
            pass
    if not worktobedone:
        newstring = stringsubmitted
    else:
        newstring = stringsubmitted.replace(worktobedone[0], worktobedone[1])
    return newstring


