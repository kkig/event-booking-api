class BookingMessages:
    INVALID_TICKET_TYPE = "One or more ticket types are invalid."
    INVALID_BOOK_FOR_EVENTS = "All ticket types must belong to the same event."
    DUPLICATE_TICKET_TYPE = "Each ticket type can only appear once in per booking."
    QUANTITY_EXCEED_CAPACITY = "Booking exceeds event capacity or ticket availability."
    INACTIVE_TICKET_TYPE = "The ticket type is not available."
    NOT_ENOUGH_TICKETS = "Not enough tickets available for the requested ticket type."
