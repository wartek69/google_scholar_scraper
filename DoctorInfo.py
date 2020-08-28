import json
class DoctorInfo:
    def __init__(self):
        self.scraped_name = 'unknown'
        self.full_name = 'unknown'
        self.year = 'unknown'
        self.speciality = 'unknown'
        self.experience = 'unknown'
        self.sub_speciality = 'unknown'
        self.languages = 'unknown'
        self.patient_experience = 'unknown'
        self.health_news_name = 'unknown'
        self.city_state = 'unknown'
        self.url = 'unknown'
        self.using_full_name = True
        self.query = 'unknown'
        self.journal = 'unknown'

    def to_csv(self):
        return '{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13}\n'.format(self.scraped_name, 
                                                            self.full_name, 
                                                            self.health_news_name,
                                                            self.year, 
                                                            self.speciality,
                                                            self.sub_speciality,
                                                            self.experience, 
                                                            self.languages,
                                                            self.city_state,
                                                            self.patient_experience,
                                                            self.url,
                                                            str(self.using_full_name),
                                                            self.journal,
                                                            self.query)
    def to_json(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        json_object = '{'

        for member in members:
            json_object += '"{0}":"{1}",'.format(member, str(getattr(self, member)).replace('"', '').replace('{', '').replace('}', ''))
        
        json_object = json_object[:-1] + '}'
        json_object = json_object.replace('\\', '')

        return json_object