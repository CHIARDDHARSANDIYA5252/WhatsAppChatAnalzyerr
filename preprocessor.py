# preprocessor.py
import re
import pandas as pd


def preprocess(data: str) -> pd.DataFrame:
    pattern = r"\[([^]]+)\] (.+?(?=\n|\Z))"
    matches = re.findall(pattern, data)
    messages_list = [list(match) for match in matches]

    df = pd.DataFrame(messages_list, columns=["date", "user_message"])

    df = df[df["date"].str.contains("AM|PM", case=False, na=False)]

    df["date"] = pd.to_datetime(
        df["date"], format="%d/%m/%y, %I:%M:%S %p", errors="coerce"
    )
    df.dropna(subset=["date"], inplace=True)

    users = []
    messages = []
    for message in df["user_message"]:
        info = re.split("([\w\W]+?):\s", message)
        if len(info) > 1:
            users.append(info[1])
            messages.append(info[2])
        else:
            users.append("group_notification")
            messages.append(info[0])

    df["user"] = users
    df["messages"] = messages
    df.drop(columns=["user_message"], inplace=True)

    df["messages"] = df["messages"].astype(str)

    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month_name()
    df["year"] = df["date"].dt.year
    df["hour"] = df["date"].dt.hour
    df["min"] = df["date"].dt.minute
    df["sec"] = df["date"].dt.second
    df["datee"] = df["date"].dt.date
    df["day_name"] = df["date"].dt.day_name()

    df["period"] = df["hour"].apply(
        lambda hour: f"{hour % 24:02d}-{(hour + 1) % 24:02d}"
    )

    return df
