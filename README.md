# National Park Campsite Finder

National Park Campsite Finder is a Python script that sends notifications when a campsite at a national park you are looking at becomes available. This helps you find a campsite even when they are all booked for the dates you are looking for. Often, people end up cancelling and you have no way of knowing. Text messages will only be sent if the availability for the campground you are looking for changes. Ideally, this script is run while there are no campsites available for the dates you are looking for and then a text message will be sent as soon as a site opens up.

## Usage

Running frontend.py will prompt you through all the arguments via the command line which may be easier than manually specifying them.

Example Text Message Created From backend.py:

<img src="img/example.jpg?raw=true" alt="drawing" width="200"/>

For setting up a Cron job, use backend.py with the argument specifications below.

```bash
usage: backend.py [-h] -p PHONE -em EMAIL -pa PASSWORD -s START -e END -c CAMPGROUND --rescan RESCAN

optional arguments:
  -h, --help            show this help message and exit
  -p PHONE, --phone PHONE
                        phone number for notification using mms
  -em EMAIL, --email EMAIL
                        email for sending text
  -pa PASSWORD, --password PASSWORD
                        password for email
  -s START, --start START
                        YYYY-MM-DD start date for search
  -e END, --end END     YYYY-MM-DD end date for search
  -c CAMPGROUND, --campground CAMPGROUND
                        campground entity id
  --rescan RESCAN       time in seconds to rescan for changes in campsite availability

backend.py "-p 12345678910@mms.cricketwireless.net -em example@gmail.com -pa password123 -s 2021-09-12 -e 2021-09-13 -c 251160 --rescan 30 "
```

## Ideas for Improvements

* setup a database to only make the API call once and keep a record of campsite availability changes
* create proper HTML/JavaScript frontend for managing these "scans" like a dashboard
* actually make a reservation when a campsite is available (not sure if this is possible)
* modify script to be able to check multiple sites at the same time.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)