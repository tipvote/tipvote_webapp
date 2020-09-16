
def cleanupdata(postmessage):
    listwords = []
    querywords = postmessage.split()
    for f in querywords:

        if len(f) > 5:

            listwords.append(f)

    resultwords = [word for word in querywords if word.lower() not in listwords]
    result = ' '.join(resultwords)
    return result