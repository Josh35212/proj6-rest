"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    start = arrow.get(brevet_start_time)

    # List containing the ACP brevet table, check for valid brevet_dist_km
    speeds = [(200, 34), (400, 32), (600, 30), (1000, 28)]
    if brevet_dist_km not in [300] + [distance for distance, speed in speeds]:
        raise ValueError("Invalid brevet distance")

    # Edge case: handle invalid negative control_dist_km
    if control_dist_km < 0:
        raise ValueError("Invalid control value")

    # Edge case: if control_dist_km = 205, brevet_dist_km = 200, calculate with 200km
    distance = min(control_dist_km, brevet_dist_km)
    # Edge case: the opening time at 0km is the brevet start time
    if distance == 0:
        return start.isoformat()

    # Main calculation logic, described in "ACP Brevet Control Times Calculator"
    elapsed_hours = 0
    previous_distance = 0
    for limit, speed in speeds:
        segment_distance = min(distance, limit) - previous_distance
        if segment_distance > 0:
            elapsed_hours += segment_distance / speed
        previous_distance = limit
        if distance <= limit:
            break
    elapsed_minutes = round(elapsed_hours * 60)
    result = start.shift(minutes=elapsed_minutes)
    return result.isoformat()


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    start = arrow.get(brevet_start_time)

    # List containing the ACP brevet table, check for valid brevet_dist_km
    speeds = [(200, 15), (400, 15), (600, 15), (1000, 11.428)]
    if brevet_dist_km not in [300] + [distance for distance, speed in speeds]:
        raise ValueError("Invalid brevet distance")

    # Edge case: handle invalid negative control_dist_km
    if control_dist_km < 0:
        raise ValueError("Invalid control value")

    # Edge case: if control_dist_km = 205, brevet_dist_km = 200, calculate with 200km
    distance = min(control_dist_km, brevet_dist_km)
    # Edge case: the closing time at 0km is one hour after brevet start time
    if distance == 0:
        return start.shift(hours=1).isoformat()

    # Special rule: a 200km brevet has closing time of 13:30 not 13:20
    if brevet_dist_km == 200 and distance == 200:
        return start.shift(hours=13, minutes=30).isoformat()

    # Special rule: a 400km brevet has closing time of 27:00 not 26:40
    if brevet_dist_km == 400 and distance == 400:
        return start.shift(hours=27, minutes=0).isoformat()

    # Oddity: controls < 60km use the "relaxed closing time" rule
    if distance < 60:
        elapsed_hours = (distance / 20) + 1
        elapsed_minutes = round(elapsed_hours * 60)
        result = start.shift(minutes=elapsed_minutes)
        return result.isoformat()

    # Main calculation logic, described in "ACP Brevet Control Times Calculator"
    elapsed_hours = 0
    previous_distance = 0
    for limit, speed in speeds:
        segment_distance = min(distance, limit) - previous_distance
        if segment_distance > 0:
            elapsed_hours += segment_distance / speed
        previous_distance = limit
        if distance <= limit:
            break
    elapsed_minutes = round(elapsed_hours * 60)
    result = start.shift(minutes=elapsed_minutes)
    return result.isoformat()
