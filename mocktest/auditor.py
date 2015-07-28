from models import *


class AuditingActions:
    _ACTION_MIN = 1

    ADDCOMPANY = 1
    ADDPOSITION = 2
    EDITPOSITION = 3
    ADDQUESTION = 4
    EDITQUESTION = 5
    MODERATEQUESTION = 6
    MODERATEMENTOR = 7
    ADDMODERATOR = 8

    actionMap = {
        ADDCOMPANY: "Added a new company",
        ADDPOSITION: "Added a new position",
        EDITPOSITION: "Edited a previous position",
        ADDQUESTION: "Added a question",
        EDITQUESTION: "Edited a question",
        MODERATEQUESTION: "Moderated a question",
        MODERATEMENTOR: "Added a mentor",
        ADDMODERATOR: "Added a moderator",
    }

    _ACTION_MAX = 8


def audit(username,
          action,
          args):
    if action < AuditingActions._ACTION_MIN or \
            action > AuditingActions._ACTION_MAX:
        raise Exception("Invalid action code")
    for key, value in args.iteritems():
        args[str(key)] = str(args.pop(key))
    auditRow = AuditLog()
    auditRow.username = username
    auditRow.action = action
    auditRow.args = args
    auditRow.info = AuditingActions.actionMap[action]
    auditRow.save()
