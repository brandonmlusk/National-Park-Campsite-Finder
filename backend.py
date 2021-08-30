from typing import DefaultDict
import requests, sched, time, smtplib, argparse
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from deepdiff import DeepDiff

s = sched.scheduler(time.time, time.sleep)


def api_call(campground_entity_id: str, start: datetime):
    formatted_date = start.strftime("%Y-%m")
    URL = f"https://www.recreation.gov/api/camps/availability/campground/{campground_entity_id}/month?start_date={formatted_date}-01T00%3A00%3A00.000Z"

    r = requests.get(
        url=URL,
        headers={
            "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        },
    )
    return r


def generate_message(availability, name):
    available_dates_msg = f"{name}:\n"
    if not bool(availability):
        available_dates_msg += "No campsites available right now!"
        return available_dates_msg

    for i, (key, value) in enumerate(availability.items()):
        available_dates_msg += f"Campsite: {key} Available Dates:"
        for dt in value:
            available_dates_msg += " " + str(dt)
        if i < len(availability) - 1:
            available_dates_msg += "\n"
    return available_dates_msg


class Campsite:
    def __init__(
        self,
        campground_entity_id: str,
        start_date: str,
        end_date: str,
        email: str,
        password: str,
        sms_gateway: str,
        name: str,
        rescan: int,
    ):
        self.campground_entity_id = campground_entity_id
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.email = email
        self.password = password
        self.sms_gateway = sms_gateway
        self.rescan = rescan
        self.name = name
        self.results = {}

    def sendText(self, body):
        # The server we use to send emails in our case it will be gmail but every email provider has a different smtp
        # and port is also provided by the email provider.
        smtp = "smtp.gmail.com"
        port = 587
        # This will start our email server
        server = smtplib.SMTP(smtp, port)
        # Starting the server
        server.starttls()
        # Now we need to login
        server.login(self.email, self.password)

        # Now we use the MIME module to structure our message.
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = self.sms_gateway
        msg.attach(MIMEText(body, "plain"))

        sms = msg.as_string()

        server.sendmail(self.email, self.sms_gateway, sms)

        # lastly quit the server
        server.quit()

    def search(self):
        current_results = self.proccess_api_call()

        if bool(DeepDiff(current_results, self.results)):
            self.results = current_results
            available_dates_msg = generate_message(self.results, self.name)
            self.sendText(available_dates_msg)

    def proccess_api_call(self):
        results = DefaultDict(list)
        responses = []
        for dt in rrule(MONTHLY, dtstart=self.start_date, until=self.end_date):
            responses.append(api_call(self.campground_entity_id, dt).json())

        for response in responses:
            if "error" in response or "campsites" not in response:
                print("Error")
                continue
            for key, value in response["campsites"].items():
                test = value["availabilities"]
                for dt in rrule(DAILY, dtstart=self.start_date, until=self.end_date):
                    formatted_date = dt.strftime("%Y-%m-%d")
                    if test[f"{formatted_date}T00:00:00Z"] == "Available":
                        results[value["site"]].append(dt.strftime("%Y-%m-%d"))
        return results


def loop(campsite: Campsite, count: int):
    campsite.search()
    count += 1
    print("End Run: " + str(count))
    s.enter(campsite.rescan, 1, loop, argument=(campsite, count))


def setup(campsite: Campsite):
    s.enter(
        0,
        1,
        loop,
        argument=(campsite, 0),
    )
    s.run()


if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding arguments
    parser.add_argument(
        "-p", "--phone", help="phone number for notification using mms", required=True
    )
    parser.add_argument("-em", "--email", help="email for sending text", required=True)
    parser.add_argument("-pa", "--password", help="password for email", required=True)
    parser.add_argument(
        "-s", "--start", help="YYYY-MM-DD start date for search", required=True
    )
    parser.add_argument(
        "-e", "--end", help="YYYY-MM-DD end date for search", required=True
    )
    parser.add_argument(
        "-c", "--campground", help="campground entity id", required=True
    )
    parser.add_argument(
        "--rescan",
        help="time in seconds to rescan for changes in campsite availability",
        required=True,
    )
    parser.add_argument(
        "--name",
        help="national park name that you are searching for (helpful if you have multiple searches running at different national parks)",
        required=True,
    )

    # Read arguments from command line
    args = parser.parse_args()

    campsite = Campsite(
        args.campground,
        args.start,
        args.end,
        args.email,
        args.password,
        args.phone,
        args.name,
        int(args.rescan),
    )

    s.enter(
        0,
        1,
        loop,
        argument=(campsite, 0),
    )
    s.run()