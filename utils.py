from urlextract import URLExtract
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
from typing import Tuple, Optional  # Import Tuple and Optional from typing module

extract = URLExtract()


def fetch_stats(
    user: str, dataframe: pd.DataFrame
) -> Tuple[int, int, int, int, int, int, int]:
    """
    Fetches statistics for a specific user or overall chat.

    Args:
        user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        Tuple[int, int, int, int, int, int, int]: A tuple containing the number of messages, words, stickers, images, videos, deleted messages, and links.
    """
    if user != "Overall":
        dataframe = dataframe[dataframe["user"] == user]

    dataframe["messages"] = dataframe["messages"].astype(str)

    num_messages = dataframe.shape[0]
    words = [word for message in dataframe["messages"] for word in message.split()]
    num_stickers = (
        dataframe["messages"].str.contains("sticker omitted", case=False).sum()
    )
    num_images = dataframe["messages"].str.contains("image omitted", case=False).sum()
    num_videos = dataframe["messages"].str.contains("video omitted", case=False).sum()
    num_deleted_msg = (
        dataframe["messages"]
        .str.contains("This message was deleted.", case=False)
        .sum()
    )
    links = [
        link for message in dataframe["messages"] for link in extract.find_urls(message)
    ]

    return (
        num_messages,
        len(words),
        num_stickers,
        num_images,
        num_videos,
        num_deleted_msg,
        len(links),
    )


def most_busy_users(dataframe: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Identifies the most active users in the chat.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        Tuple[pd.Series, pd.DataFrame]: A tuple containing the top 7 users and a DataFrame with user activity percentages.
    """
    x = dataframe["user"].value_counts().head(7)
    df1 = (
        round((dataframe["user"].value_counts() / dataframe.shape[0]) * 100, 2)
        .reset_index()
        .rename(columns={"count": "percent"})
    )
    df2 = dataframe["user"].value_counts()
    df = pd.merge(df1, df2, on="user")
    return x, df


def create_wordcloud(selected_user: str, dataframe: pd.DataFrame) -> WordCloud:
    """
    Creates a word cloud for the messages of a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        WordCloud: A WordCloud object.
    """
    try:
        with open("stopwords.txt", "r") as f:
            stop_words = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("The stopwords.txt file was not found.")

    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    if "messages" not in dataframe.columns:
        raise KeyError("The 'messages' column is missing in the DataFrame.")

    ignore_text = [
        "image omitted",
        "This message was deleted.",
        "video omitted",
        "sticker omitted",
        "gif omitted",
    ]
    df_filtered = dataframe[
        ~dataframe["messages"].apply(
            lambda x: any(substring in x for substring in ignore_text)
        )
    ]

    def remove_stop_words(message: str) -> str:
        return " ".join(
            word for word in message.lower().split() if word not in stop_words
        )

    wc = WordCloud(width=600, height=600, min_font_size=10, background_color="black")
    df_filtered["messages"] = df_filtered["messages"].apply(remove_stop_words)
    df_wc = wc.generate(df_filtered["messages"].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Finds the most common words used by a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        pd.DataFrame: A DataFrame containing the most common words and their counts.
    """
    try:
        with open("stopwords.txt", "r") as f:
            stop_words = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("The stopwords.txt file was not found.")

    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    if "messages" not in dataframe.columns:
        raise KeyError("The 'messages' column is missing in the DataFrame.")

    ignore_text = [
        "image omitted",
        "This message was deleted.",
        "video omitted",
        "sticker omitted",
        "gif omitted",
    ]
    df_filtered = dataframe[
        ~dataframe["messages"].apply(
            lambda x: any(substring in x for substring in ignore_text)
        )
    ]

    words = [
        word
        for message in df_filtered["messages"]
        for word in message.lower().split()
        if word not in stop_words
    ]
    most_common_df = pd.DataFrame(Counter(words).most_common(25))
    return most_common_df


def monthly_timeline(selected_user: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a monthly timeline of messages for a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        pd.DataFrame: A DataFrame containing the monthly timeline of messages.
    """
    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    timeline = dataframe.groupby(["year", "month"]).count()["messages"].reset_index()
    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)
    return timeline


def daily_timeline(selected_user: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a daily timeline of messages for a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        pd.DataFrame: A DataFrame containing the daily timeline of messages.
    """
    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    timeline = dataframe.groupby("datee").count()["messages"].reset_index()
    return timeline


def week_activity(selected_user: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes the weekly activity of a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        pd.DataFrame: A DataFrame containing the weekly activity.
    """
    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    day_timeline = dataframe["day_name"].value_counts().reset_index()
    return day_timeline


def month_activity(selected_user: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes the monthly activity of a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        pd.DataFrame: A DataFrame containing the monthly activity.
    """
    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    month_time = dataframe["month"].value_counts().reset_index()
    return month_time


def activity_heatmap(
    selected_user: str, dataframe: pd.DataFrame
) -> Optional[pd.DataFrame]:
    """
    Creates a heatmap of activity for a selected user.

    Args:
        selected_user (str): The user to filter by. Use "Overall" for all users.
        dataframe (pd.DataFrame): The DataFrame containing the chat data.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the activity heatmap, or None if the DataFrame is empty.
    """
    if selected_user != "Overall":
        dataframe = dataframe[dataframe["user"] == selected_user]

    if dataframe.empty:
        return None

    dataframe["period"] = pd.Categorical(
        dataframe["period"],
        categories=[f"{i:02d}-{(i + 1) % 24:02d}" for i in range(24)],
        ordered=True,
    )
    pivot_activity = dataframe.pivot_table(
        index="day_name", columns="period", values="messages", aggfunc="count"
    ).fillna(0)

    return pivot_activity
