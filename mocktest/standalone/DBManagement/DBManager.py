import os
import re
import django
import inspect
import mocktest.models
from django.db import connections
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist


def __convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


classNames = [__convert(x[0])
              for x in filter(
                lambda x: issubclass(x[1], Model) and
                x[0] != "Model",
                inspect.getmembers(
                    mocktest.models,
                    inspect.isclass)
                )
              ]


def __wipeTable(tableName, cursor=None):
    print "Wiping Table %s" % tableName
    close = False
    if not cursor:
        cursor = connections["cassandra"].cursor()
        close = True
    try:
        cursor.execute("""
            DROP TABLE %s
        """ % tableName)
        print "Table %s wiped successfuly" % tableName
        if tableName == "users":
            __cleanAuthUsers()
    except Exception, e:
        print "Encountered Exception", str(e), "Proceeding"
    finally:
        if close:
            cursor.close()


def wipeTable():
    print "List of tables are:"
    for klass in classNames:
        print klass
    print ""
    tableName = raw_input("Enter the table name:")
    __wipeTable(tableName)


def wipeDatabase():
    print "Wiping All tables in the system"
    for klass in classNames:
        __wipeTable(klass)


def __cleanAuthUsers():
    print "Clearing users used for authentication"
    authUsers = User.objects.all()
    for authUser in authUsers:
        authUser.delete()


def createAdmin():
    print "Checking if admin User Exist"
    try:
        adminUser = mocktest.models.Users.objects.get(username='admin')
        if adminUser:
            print "Admin User already exist. Nothing to do"
            return
    except DoesNotExist:
        pass
    print "Creating Admin User"
    adminUser = mocktest.models.Users()
    adminUser.username = 'admin'
    adminUser.password = 'admin'
    adminUser.firstname = 'Administrator'
    adminUser.lastname = 'Administrator'
    adminUser.email = 'hashincludetest@gmail.com'
    adminUser.isinternal = True
    adminUser.ianatimezone = 'America/Phoenix'
    adminUser.save()
    try:
        authUser = User.objects.get(username='admin',
                                    password='mockingsite')
    except User.DoesNotExist:
        authUser = User()
        authUser.username = 'admin'
        authUser.password = 'mockingsite'
        authUser.save()
    try:
        moderatorGrp = Group.objects.get(name='Moderators')
    except Group.DoesNotExist:
        moderatorGrp = Group(name='Moderators')
        moderatorGrp.save()
    authUser.groups.add(moderatorGrp)
    authUser.is_staff = True
    authUser.is_superuser = True
    authUser.save()
    moderator = mocktest.models.Moderators()
    moderator.username = adminUser.username
    moderator.firstname = adminUser.firstname
    moderator.lastname = adminUser.lastname
    moderator.email = adminUser.email
    moderator.phone = adminUser.phone
    moderator.save()
    print "Admin user created successfuly"


def dropAdmin():
    print "Dropping (\"admin\") admin user"
    try:
        adminUser = mocktest.models.Users.objects.get(username='admin')
        adminUser.delete()
    except DoesNotExist:
        pass
    try:
        moderator = mocktest.models.Moderators.objects.get(username='admin')
        moderator.delete()
    except DoesNotExist:
        pass
    print "Admin user dropped successfuly"


def createTables():
    print "Creating tables. Make sure $MOCKINGBIRDPATH is defined"
    print "Current $MOCKINGBIRDPATH is"
    os.system("echo $MOCKINGBIRDPATH;")
    ip = raw_input("Do you want to proceed [y/n]: ")
    if ip.strip().lower() == "y":
        os.system("cd $MOCKINGBIRDPATH; python manage.py sync_cassandra")
    else:
        print "Nothing to do."


def main():
    #os.environ["DJANGO_SETTINGS_MODULE"] = "mockingsite.settings"
    django.setup()


def interface():
    while True:
        print ""
        print "Please choose an option below [0 - 5]"
        print "1) Wipe the database"
        print "2) Create Admin User"
        print "3) Drop (\"admin\") Admin User"
        print "4) Wipe Single Table"
        print "5) Create Tables"
        print "0) Exit"
        print ""
        try:
            choice = int(input())
            if choice == 1:
                wipeDatabase()
                continue
            if choice == 2:
                createAdmin()
                continue
            if choice == 3:
                dropAdmin()
                continue
            if choice == 4:
                wipeTable()
                continue
            if choice == 5:
                createTables()
            if choice == 0:
                break
            print "Enter a valid choice [0 - 5]"
        except Exception, e:
            print "Exception Occured:", str(e), "Proceeding"


if __name__ == '__main__':
    main()
    from django.contrib.auth.models import User
    from django.contrib.auth.models import Group
    interface()
