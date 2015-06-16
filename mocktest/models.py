# from django.db import models

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from datetime import datetime
import utils

# Create your models here.


class Users(Model):
    username = columns.Text(primary_key=True)
    password = columns.Text(required=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()
    fbid = columns.Text()
    rating = columns.Integer(primary_key=True,
                             clustering_order="DESC", default=1200)
    ctime = columns.DateTime(default=datetime.now)
    mtime = columns.DateTime(default=datetime.now)

# Below Models adopt the Wide-Row design paradigm


class Tests(Model):
    testid = columns.TimeUUID(primary_key=True)
    testname = columns.Text(static=True)
    username = columns.Text(static=True)
    retrorating = columns.Integer(static=True)  # Needs a better name
    # companyid = columns.TimeUUID(static=True)
    # positionid = columns.TimeUUID(static=True)
    companyname = columns.Text(static=True)
    positionname = columns.Text(static=True)
    # STATE: 0:Not Begun, 1:In progress, 2:Completed
    state = columns.Integer(static=True)
    totalquestions = columns.Integer(static=True)
    questionsanswered = columns.Integer(static=True)
    currentquestion = columns.Integer(static=True)
    isevaluated = columns.Boolean(static=True)
    totalmarks = columns.Float(static=True)
    scoredmarks = columns.Float(static=True)
    teststarttime = columns.DateTime(static=True)
    testendtime = columns.DateTime(static=True)
    userstarttime = columns.DateTime(static=True)
    userendtime = columns.DateTime(static=True)
    ctime = columns.DateTime(default=datetime.now)
    mtime = columns.DateTime(default=datetime.now)
    questionnum = columns.Integer(primary_key=True,
                                  required=True,
                                  clustering_order="ASC")
    questionid = columns.TimeUUID(required=True)
    question = columns.Text(required=True)
    questiontype = columns.Integer(required=True, default=3)
    givenanswer = columns.Text()
    correctanswer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()


# class PendingEvaluationCompany(Model):
#     pass


# class PendingEvaluationPosition(Model):
#     pass


# class PendingEvaluationCompanyPosition(Model):
#     pass


# class PendingEvaluationPositionCompany(Model):
#     pass


class UserScheduledTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text(required=True, default="Test " +
                            datetime.now().strftime("%c"))
    # companyid = columns.TimeUUID(required=True)
    # positionid = columns.TimeUUID(required=True)
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    teststarttime = columns.DateTime(required=True)
    testendtime = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)


class UserSavedTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text(required=True, default="Test " +
                            datetime.now().strftime("%c"))
    # companyid = columns.TimeUUID(required=True)
    # positionid = columns.TimeUUID(required=True)
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)


class UserCompany(Model):
    username = columns.Text(primary_key=True)
    # companyid = columns.TimeUUID(primary_key=True)
    companyname = columns.Text(primary_key=True)


class UserCompanyTests(Model):
    username = columns.Text(partition_key=True)
    # companyid = columns.TimeUUID(partition_key=True)
    companyname = columns.Text(partition_key=True)
    # positionid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    positionname = columns.Text(primary_key=True, clustering_order="DESC")
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)


class UserPosition(Model):
    username = columns.Text(primary_key=True)
    # positionid = columns.TimeUUID(primary_key=True)
    positionname = columns.Text(primary_key=True)


class UserPositionTests(Model):
    username = columns.Text(partition_key=True)
    # positionid = columns.TimeUUID(partition_key=True)
    positionname = columns.Text(partition_key=True)
    # companyid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    companyname = columns.Text(primary_key=True, clustering_order="DESC")
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)


class UserTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    # companyid = columns.TimeUUID(required=True)
    companyname = columns.Text(required=True)
    # positionid = columns.TimeUUID(required=True)
    positionname = columns.Text(required=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)


class UserQuestion(Model):
    username = columns.Text(partition_key=True)
    # companyid = columns.TimeUUID(partition_key=True)
    # positionid = columns.TimeUUID(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    questionid = columns.TimeUUID(primary_key=True, clustering_order="DESC")


class CompanyPosition(Model):
    # companyid = columns.TimeUUID(primary_key=True)
    companyname = columns.Text(primary_key=True)
    # positionid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    positionname = columns.Text(primary_key=True)


class PositionCompany(Model):
    # positionid = columns.TimeUUID(primary_key=True)
    positionname = columns.Text(primary_key=True)
    # companyid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    companyname = columns.Text(primary_key=True)


# class PositionRevLookup(Model):
#    positionname = columns.Text(primary_key=True)
#    positionid = columns.TimeUUID(required=True)


# class CompanyRevLookup(Model):
#    companyname = columns.Text(primary_key=True)
#    companyid = columns.TimeUUID(required=True)


class MentorCompanyPosition(Model):
    username = columns.Text(partition_key=True)
#    companyid = columns.TimeUUID(primary_key=True)
#    positionid = columns.TimeUUID(primary_key=True)
    companyname = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)


class QuestionBank(Model):
    # companyid = columns.TimeUUID(partition_key=True)
    # positionid = columns.TimeUUID(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    questionid = columns.TimeUUID(primary_key=True,
                                  required=True,
                                  clustering_order="DESC")
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=1200)


class RawQuestionBank(Model):
    # companyid = columns.TimeUUID(partition_key=True)
    # positionid = columns.TimeUUID(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    questionid = columns.TimeUUID(primary_key=True,
                                  required=True,
                                  clustering_order="DESC")
    questiontype = columns.Integer(required=True)
    url = columns.Text(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)

    def __str__(self):
        return self.question + "\n\n" + self.answer + "\n\n"
