from django.core.mail import EmailMessage


class PostOffice:

    CODE_MIN = 1

    NEW_USER = 1
    NEW_MENTOR = 2
    NEW_MODERATOR = 3
    NEW_USER_MENTOR = 4
    TEST_ABOUT_TO_START = 6
    EVALUATION_DONE = 7
    MENTOR_APPROVED = 8
    MODERATOR_APPROVED = 9

    CODE_MAX = 9

    greetingCards = {}
    greetingCards[NEW_USER] = {}
    greetingCards[NEW_USER]['SUBJECT'] = "User Verification"
    greetingCards[NEW_USER]['CONTENT'] = \
        "Hi %(username)s,\nPlease click or paste the following URL in your " +\
        "browser " +\
        "to verify your e-mail and activate your hashincludetest " +\
        "user account \n\n %(verificationURL)s \n\nThanks for signing up " +\
        "with us."
    greetingCards[NEW_MENTOR] = {}
    greetingCards[NEW_MENTOR]['SUBJECT'] = "Mentor Verification"
    greetingCards[NEW_MENTOR]['CONTENT'] = \
        "Hi %(username)s,\nPlease click or paste the following URL in your" +\
        " browser " +\
        "to verify your e-mail and activate your hashincludetest " +\
        "mentor account \n\n %(verificationURL)s \n\nAfter verification " +\
        "please grant " +\
        "us three to five business days to verify your account. " +\
        "We will get in touch with you very soon.\n\n" +\
        "Thanks for signing up with us."
    greetingCards[NEW_MODERATOR] = {}
    greetingCards[NEW_MODERATOR]['SUBJECT'] = "Moderator Verification"
    greetingCards[NEW_MODERATOR]['CONTENT'] = \
        "Hi %(username)s,\nPlease click or paste the following URL in your " +\
        "browser " +\
        "to verify your e-mail and activate your hashincludetest " +\
        "moderator account \n\n %(verificationURL)s \n\nAfter verification " +\
        "please grant " +\
        "us three to five business days to verify your account. " +\
        "We will get in touch with you very soon.\n\n" +\
        "Thanks for signing up with us."
    greetingCards[NEW_USER_MENTOR] = {}
    greetingCards[NEW_USER_MENTOR]['SUBJECT'] = "Verification"
    greetingCards[NEW_USER_MENTOR]['CONTENT'] = \
        "Hi %(username)s,\nPlease click or paste the following URL in your " +\
        "browser " +\
        "to verify your e-mail and activate your hashincludetest " +\
        "account \n\n %(verificationURL)s \n\n. Since you have also " +\
        "registered as a " +\
        "mentor, please grant us three to five business days to " +\
        "verify your account. In the mean time you can login as a standard " +\
        "user and take tests." +\
        "We will get in touch with you very soon.\n\n" +\
        "Thanks for signing up with us."
    greetingCards[TEST_ABOUT_TO_START] = {}
    greetingCards[TEST_ABOUT_TO_START]['SUBJECT'] = \
        "Your test is to start shortly"
    greetingCards[TEST_ABOUT_TO_START]['CONTENT'] = \
        "Hi %(username)s,\nThe test you scheduled for company " +\
        "\"%(companyName)s\" and position \"%(positionName)s\" is to start " +\
        "by %(startTime)s.\n\n Here is a direct link to the test.\n\n" +\
        "%(testURL)s\nWe wish you all the best."
    greetingCards[EVALUATION_DONE] = {}
    greetingCards[EVALUATION_DONE]['SUBJECT'] = \
        "Your test is evaluated"
    greetingCards[EVALUATION_DONE]['CONTENT'] = \
        "Hi %(username)s,\nThe test you took on %(startTime)s for company " +\
        "\"%(companyName)s\" and position \"%(positionName)s\" has been " +\
        "evaluated.\n\n Here is a direct link to the result.\n\n" +\
        "%(resultURL)s\n."
    greetingCards[MENTOR_APPROVED] = {}
    greetingCards[MENTOR_APPROVED]['SUBJECT'] = \
        "Your request to be a mentor is approved"
    greetingCards[MENTOR_APPROVED]['CONTENT'] = \
        "Hi %(username)s,\nYour request to be a mentor at " +\
        "hashincludetest.com has  been approved. We are proud to have " +\
        "you join our team.\nPlease head over to %(mentorURL)s to start " +\
        "mentoring. People needing your advice are waiting out there"
    greetingCards[MODERATOR_APPROVED] = {}
    greetingCards[MODERATOR_APPROVED]['SUBJECT'] = \
        "Your request to be a moderator is approved"
    greetingCards[MODERATOR_APPROVED]['CONTENT'] = \
        "Hi %(username)s,\nYour request to be a moderator at " +\
        "hashincludetest.com has  been approved. We are happy to have " +\
        "you join our team.\nPlease head over to %(adminURL)s to start " +\
        "moderating. Please make sure you read terms and conditions in " +\
        "that same page. We hope you have a good time with us."


def sendMail(emailAddr, code, _dict):
    if code < PostOffice.CODE_MIN or \
       code > PostOffice.CODE_MAX:
        raise ValueError("Invalid code %s" % str(code))
    message = PostOffice.greetingCards[code]['CONTENT'] % _dict
    email = EmailMessage(
                PostOffice.greetingCards[code]['SUBJECT'],
                message,
                to=[emailAddr])
    email.send()
