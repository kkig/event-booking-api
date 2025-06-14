from common.choices import EventStatus


class EventMessages:
    NOT_EVENT_OWNER = "You are not the organizer of this event."
    START_TIME_IS_PAST = "Start time cannot be in the past."
    END_TIME_IS_PAST = "End time cannot be in the past."
    END_TIME_SHOULD_BE_AFTER_START = "End time must be after start time."
    INVALID_STATUS_ON_CREATE = f"Only '{EventStatus.UPCOMING}' events can be created."


class EventTypeMessages:
    INVALID_AVAILABILITY_ON_CREATE = "Quantity must be at least 1 when creating."
