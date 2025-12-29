def calculate_progress(current_time, total_duration):
    if total_duration == 0:
        return
    return min((current_time / total_duration) * 100, 100)
