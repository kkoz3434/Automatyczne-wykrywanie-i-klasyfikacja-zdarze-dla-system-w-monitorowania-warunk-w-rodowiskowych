from datetime import datetime, timezone


def get_today_date_string():
    today_utc = datetime.utcnow()
    end_of_day_utc = today_utc.replace(hour=23, minute=59, second=59)
    utc_offset = timezone.utc.utcoffset(today_utc)
    formatted_date_string = end_of_day_utc.replace(tzinfo=timezone(utc_offset)).strftime(
        '%Y-%m-%d %H:%M:%S') + "+00:00"
    return formatted_date_string


def get_minimum_date_string():
    today_utc = datetime.min
    end_of_day_utc = today_utc.replace(hour=23, minute=59, second=59)
    utc_offset = timezone.utc.utcoffset(today_utc)
    formatted_date_string = end_of_day_utc.replace(tzinfo=timezone(utc_offset)).strftime(
        '%Y-%m-%d %H:%M:%S') + "+00:00"
    return formatted_date_string
