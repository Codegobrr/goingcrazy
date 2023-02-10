

class Public:
    count_id = 0

    def __init__(self, name, email, no, enquiry):
        self.__name = name
        self.__email = email
        self.__phone_number = no
        self.__enquiry = enquiry
        Public.count_id += 1
        self.__id = Public.count_id

    def set_name(self, name):
        self.__name = name

    def set_email(self, email):
        self.__email = email

    def set_phone_number(self, no):
        self.__phone_number = no

    def set_enquiry(self, enquiry):
        self.__enquiry = enquiry

    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_phone_number(self):
        return self.__phone_number

    def get_enquiry(self):
        return self.__enquiry

    def get_id(self):
        return self.__id


class Private:
    count_id = 0

    def __init__(self, name, gender, level, day, timing, subject, tutor, topic, rating, feedback):
        self.__name = name
        self.__gender = gender
        self.__subject = subject
        self.__timing = timing
        self.__tutor = tutor
        self.__topic = topic
        self.__level = level
        self.__day = day
        self.__feedback = feedback
        self.__rating = rating
        Private.count_id += 1
        self.__id = Private.count_id

    def set_name(self, name):
        self.__name = name

    def set_topic(self, topic):
        self.__topic = topic

    def set_timing(self, timing):
        self.__timing = timing

    def set_subjects(self, subject):
        self.__subject = subject

    def set_day(self, day):
        self.__day = day

    def set_tutor(self, tutor):
        self.__tutor = tutor

    def set_gender(self, gender):
        self.__gender = gender

    def set_level(self, level):
        self.__level = level

    def set_feedback(self, feedback):
        self.__feedback = feedback

    def set_rating(self, rating):
        self.__rating = rating

    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def get_day(self):
        return self.__day

    def get_subject(self):
        return self.__subject

    def get_timing(self):
        return self.__timing

    def get_tutor(self):
        return self.__tutor

    def get_level(self):
        return self.__level

    def get_feedback(self):
        return self.__feedback

    def get_id(self):
        return self.__id

    def get_rating(self):
        return self.__rating

    def get_gender(self):
        return self.__gender

    def get_topic(self):
        return self.__topic


class Yeet:
    def __init__(self, name, gender, level, email):
        self.__name = name
        self.__gender = gender
        self.__level = level
        self.__email = email


    def set_name(self, name):
        self.__name = name

    def set_gender(self, gender):
        self.__gender = gender

    def set_level(self, level):
        self.__level = level

    def set_email(self, email):
        self.__email = email


    def set_name(self, name):
        self.__name = name

    def get_gender(self):
        return self.__gender

    def get_level(self):
        return self.__level

    def get_email(self):
        return self.__email
