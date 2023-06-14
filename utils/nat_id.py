from datetime import date
import hashlib

class Parse_NID():
    def __init__(self):
        self.fname=""
        self.lname=""
        self.mname=""
        self.gender=""
        self.birth_date=""
        self.nat_id=""
        self.print_dob=""
        self.val=""

    def parse_national_id(self,text):
        val = text.split('~')
        if len(val) == 12:
            if len(val[6].split(', ')) > 1:
                self.fname, self.mname = val[6].split(', ')
            else:
                self.fname = val[6]
                self.mname = ''
            self.lname = val[4]
            self.gender = str(val[8]).upper()
            raw_dob = val[9]
            self.nat_id = str(val[5])

            dateOfBirth = str(raw_dob).split(" ")
            day = dateOfBirth[0]
            year = dateOfBirth[2]
            month = dateOfBirth[1]

            month_var = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9,
                        "OCT": 10, "NOV": 11, "DEC": 12}
            num_month = month_var[month.upper()]

            self.birth_date = date(int(year), num_month, int(day))

            self.print_dob = year + "-" + str(num_month) + "-" + day

            result = {"first_name": self.fname,"middle_name":self.mname, "last_name": self.lname, "gender": self.gender,
                    "nation_id": self.nat_id, "dob": self.birth_date, "printable_dob": self.print_dob}

            #print(result)
            return result