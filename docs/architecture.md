# Architecture (Concurrency)

To prevent overbooking under concurrent booking attempts:

- All booking creations run inside `transaction.atomic()` blocks.
- Ticket types and events are locked with `select_for_update()` to ensure row-level locking.
- Ticket availability and event capacity are checked and updated atomically.
- Automated tests simulate concurrent booking attempts with multiple threads, ensuring that only one booking succeeds when capacity is limited.


## Booking Flow

[Mermaid sequence diagram](https://mermaid.live) that visualizes booking creation flow with concurrency control.

<details>
sequenceDiagram
    participant A as Attendee
    participant C as API Server
    participant D as Database

    A->>C: POST /api/bookings/
    C->>C: Begin transaction.atomic()
    C->>D: SELECT TicketType FOR UPDATE
    C->>D: SELECT Event FOR UPDATE
    C->>D: Check availability & capacity

    alt Tickets Available
        C->>D: Create Booking
        C->>D: Set Booking status to CONFIRMED
        C->>D: Decrement TicketType.quantity_available
        C->>D: Increment TicketType.quantity_sold
        C->>D: Commit Transaction
        C-->>A: 201 Created (Booking Confirmed)
    else Sold Out
        C->>D: Rollback Transaction
        C-->>A: 400 Bad Request (Sold Out)
    end

</details>

### Booking Cancellation Flow

[Mermaid sequence diagram](https://mermaid.live) that visualizes booking cancellation flow with concurrency control.

<details>
sequenceDiagram
    participant A as Attendee
    participant C as API Server
    participant D as Database

    A->>C: PUT /api/bookings/:id/
    C->>C: Check auth and ownership
    C->>D: Begin transaction.atomic()
    C->>D: Lock Booking (SELECT ... FOR UPDATE)
    C->>D: Check Booking status
    alt Already cancelled
        C-->>A: 400 Bad Request (already cancelled)
    else Valid cancellation
        C->>D: Update Booking status to CANCELLED
        C->>D: Increment TicketType.quantity_available
        C->>D: Decrement TicketType.quantity_sold
        C->>D: Commit transaction
        C-->>A: 200 OK (cancelled)
    end

</details>


## Concurrency Test Suite

A key aspect of this API is its robust handling of concurrent booking requests. The test suite includes specific tests designed to validate the system's behavior under high-stress, simultaneous interactions.

These tests utilize Python's `threading` module within Pytest to simulate multiple users attempting to book tickets concurrently. They ensure that:

- **No Overbooking:** Even with multiple simultaneous requests, the system prevents tickets from being oversold beyond available capacity
- **Race Condition Prevention:** Scenarios like two users attempting to book the very last available ticket are handled correctly, with only one request succeeding.
- **Shared Capacity Management:** Tests cover situations where different ticket types contribute to a single event's overall capacity, ensuring accurate availability updates across types.
- **Atomic Operations:** Verifies that critical operations (booking creation, quantity updates, cancellations) are atomic and concurrency-safe, leveraging PostgreSQL's row-level locking (`select_for_update()`) and Django's `transaction.atomic()` blocks.
- **Cancellation Releasing Tickets:** Confirms that cancelling a booking correctly frees up ticket availability for other users to book immediately.

These dedicated concurrency tests provide strong confidence in the API's reliability under real-world usage patterns.
