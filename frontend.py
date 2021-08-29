import requests
import backend


class SelectionResponse:
    def __init__(self, selection: int, response):
        self.selection = selection
        self.response = response


def get_national_park_suggestions(search):
    suggestionURL = "https://www.recreation.gov/api/search/suggest"

    r = requests.get(
        url=suggestionURL,
        params={"geocoder": "true", "q": search},
        headers={
            "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        },
    )
    return r


def get_national_park_campsites(parent_asset_id):
    suggestionURL = "https://www.recreation.gov/api/search"

    r = requests.get(
        url=suggestionURL,
        params={
            "fq": [
                f"parent_asset_id%3A{parent_asset_id}",
                f"entity_type%3Acampground",
                f"campsite_type_of_use%3AOvernight",
                f"campsite_type_of_use%3ADay",
                f"campsite_type_of_use%3Ana",
            ],
            "size": f"1000",
            "sort": f"score",
        },
        headers={
            "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        },
    )
    return r


def search_prompt():
    search = input("Search for campgrounds, tours, or other recreation activities:")

    response = get_national_park_suggestions(search).json()["inventory_suggestions"]

    return response


def iterate_and_select(response):
    print("\nResults...\n")
    for idx, val in enumerate(response):
        print(str(idx) + ": " + val["name"])

    selection = input(
        "\nMake selection by choosing the number corresponding to your desired activity or -1 to search again:"
    )
    return int(selection)


def prompt_loop(msg):
    selection = "-1"
    while selection == "-1":
        selection = input(msg)
    return selection


if __name__ == "__main__":
    selection = -1
    while (selection < 0) or (selection >= len(response)):
        response = search_prompt()
        selection = iterate_and_select(response)

    id = response[selection]["entity_id"]
    response = get_national_park_campsites(id).json()["results"]

    selection = -1
    while (selection < 0) or (selection >= len(response)):
        selection = iterate_and_select(response)

    campground_entity_id = response[selection]["entity_id"]
    sms_gateway = prompt_loop("\nEnter Phone Number to send an alert text to: ")
    email = prompt_loop("\nEnter Email to send the alert text from: ")
    email_password = prompt_loop("\nEnter Email password: ")
    start_date = prompt_loop("\nEnter start date (YYYY-MM-DD) for your trip: ")
    end_date = prompt_loop(
        "\nEnter the end date (YYYY-MM-DD) for the last night you need a campsite for: "
    )
    rescan = prompt_loop(
        "\nEnter amount of time between checking for a new campsite (scan for availability every 30 sec, 1 min etc): "
    )
    campsite = backend.Campsite(
        campground_entity_id,
        start_date,
        end_date,
        email,
        email_password,
        sms_gateway,
        int(rescan),
    )
    backend.setup(campsite)
