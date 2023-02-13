from tiktokapipy.api import TikTokAPI
from datetime import datetime, date
import csv

def to_date(datetime_obj):
    return date(datetime_obj.year, datetime_obj.month, datetime_obj.day)

def parse_date(map, field):
    if map[field] != "":
        try:
            map[field] = to_date(datetime.strptime(map[field], "%d.%m.%Y"))
        except ValueError:
            print("Date format must be DD.MM.YYYY")

def median(numbers):
    if len(numbers) == 0:
        return 0
    numbers.sort()
    if len(numbers) % 2 == 0:
        return (numbers[len(numbers) // 2 - 1] + numbers[len(numbers) // 2]) / 2
    else:
        return numbers[len(numbers) // 2]

def average(numbers):
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)

def read_configs(name, map):
    with open(name, "r") as file:
        for line in file:
            parts = line.split("=")
            key = parts[0].strip()
            value = parts[1].strip()
            if key in config_map:
                map[key] = value
                print(f"The value for the config {key} set to {value}.")
            else:
                print(f"The key {key} is not in config_map.")

def parse_configs(map):
    map["video_amount"] = int(map["video_amount"])
    parse_date(map, "date_start")
    parse_date(map, "date_end")
    if (map["date_start"] != "" and map["date_end"] != "" and map["date_start"] > map["date_end"]):
        print(f"date_start {map['date_start']} > date_end {map['date_end']}")
        print("dates ignored")
        map["date_start"] = ""
        map["date_end"] = ""

def read_inputs(name, storage):
    with open(name, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith('@'):
                data = {"Account": line}
                storage.append(data)
            else:
                print(f"Invalid account provided: {line}")

def main_logic(storage, config):
    print()
    for data in storage:
        print(f"Analysing {data['Account']}")
        with TikTokAPI() as api:
            user = api.user(data['Account'][1:])
            count = 0
            comments = []
            likes = []
            views = []
            shares = []
            for video in user.videos:
                create_date = to_date(video.create_time)
                if count >= config["video_amount"]:
                    print(f"    Reached maximum amount for the current user.")
                    break
                if config["date_end"] != "" and config["date_end"] < create_date:
                    print(f"    Video {video.desc} skipped because create_date = {create_date} < date_end = {config['date_end']}")
                    continue
                if config["date_start"] != "" and config["date_start"] > create_date:
                    print(f"    Stop analysing current user because video {video.desc} create_date = {create_date} > date_start = {config['date_start']}")
                    break
                print(f"    Analysing video {video.desc}")
                count += 1
                data["video " + str(count) + " create time"] = str(video.create_time)
                data["video " + str(count) + " desc"] = str(video.desc)
                data["video " + str(count) + " comments"] = str(video.stats.comment_count)
                data["video " + str(count) + " likes"] = str(video.stats.digg_count)
                data["video " + str(count) + " views"] = str(video.stats.play_count)
                data["video " + str(count) + " shares"] = str(video.stats.share_count)
                comments.append(video.stats.comment_count)
                likes.append(video.stats.digg_count)
                views.append(video.stats.play_count)
                shares.append(video.stats.share_count)
            for i in range(count + 1, config["video_amount"] + 1):
                data["video " + str(i) + " create time"] = ""
                data["video " + str(i) + " desc"] = ""
                data["video " + str(i) + " comments"] = ""
                data["video " + str(i) + " likes"] = ""
                data["video " + str(i) + " views"] = ""
                data["video " + str(i) + " shares"] = ""
            data["total videos in period"] = str(count)
            data["total comments"] = str(sum(comments))
            data["total likes"] = str(sum(likes))
            data["total views"] = str(sum(views))
            data["total shares"] = str(sum(shares))
            data["avg comments"] = str(average(comments))
            data["avg likes"] = str(average(likes))
            data["avg views"] = str(average(views))
            data["avg shares"] = str(average(shares))
            data["med comments"] = str(median(comments))
            data["med likes"] = str(median(likes))
            data["med views"] = str(median(views))
            data["med shares"] = str(median(shares))
    print("analysis end, creating file")

def write_csv(name, storage):
    if len(storage) == 0:
        print("No data for file")
        return
    header = []
    longest = 0
    for data in storage:
        if len(data) > longest:
            longest = len(data)
            for key, value in data.items():
                header.append(key)
    with open(name, "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        #write head
        writer.writerow(header)
        for data in storage:
            row = []
            for col in header:
                row.append(data[col])
            writer.writerow(row)

#globals
input_file = "TikTokStat.input"
config_file = "TikTokStat.conf"
output_file = "TikTokStat.csv"
config_map = {
    "video_amount": "10",
    "date_start": "",
    "date_end": ""
}
storage = []

print("---------- Start ------------")
print()

read_configs(config_file, config_map)
parse_configs(config_map)
read_inputs(input_file, storage)
main_logic(storage, config_map)
write_csv(output_file, storage)

print()
print("---------- End ------------")