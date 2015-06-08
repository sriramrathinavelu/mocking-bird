from careerCupScrapper import careerCupScrapper
import os
import django


def getInstance(url, companyName, positionName):
    if url and companyName and positionName:
        if (careerCupScrapper.isSupported(url=url)):
            return careerCupScrapper(url=url,
                                     companyName=companyName,
                                     positionName=positionName)
    else:
        raise Exception("Need url, companyName and positionName parameter")


def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "mockingsite.settings"
    django.setup()

if __name__ == '__main__':
    main()
