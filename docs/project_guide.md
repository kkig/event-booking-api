# Project Guideline: Event Ticketing/Booking System API

**Core Goal:** Build a robust backend API that allows users to browse events, select ticket types, make bookings, and manage their orders. It should also allow event organizers to manage their events.

---

### Phase 0: Planning & Setup (The Foundation)

**Learning Objectives:**

- **Requirements Gathering:** How to break down a high-level idea into concrete features.
- **Database Design:** Translating business requirements into a structured data model.
- **Technology Selection:** Understanding the pros and cons of different tools for a specific project.
- **Project Setup:** Setting up a professional development environment.

**Steps:**

1.  **Define Core Features (Minimal Viable Product - MVP):**

    - **Public (Unauthenticated) Access:**
      - View all events.
      - View details of a specific event (including available ticket types, prices, dates).
      - Search/filter events.
    - **Authenticated User (Attendee) Features:**
      - Register/Login.
      - Book tickets for an event.
      - View their booked tickets/orders.
      - Cancel a booking (within a certain timeframe).
    - **Authenticated User (Organizer) Features:**
      - Register/Login (perhaps a separate registration flow or role).
      - Create, Read, Update, Delete (CRUD) their own events.
      - Manage ticket types for their events.
      - View bookings for their events.

2.  **Choose Your Tech Stack:**

    - **Backend Framework:** Node.js (Express, NestJS), Python (Django, FastAPI, Flask), Java (Spring Boot), Go (Gin, Echo), Ruby on Rails, etc. Choose what you're most comfortable with or eager to learn deeply.
    - **Database:**
      - **SQL (Recommended for this project):** PostgreSQL or MySQL. Excellent for managing relational data (Users, Events, Tickets, Bookings) and handling complex transactions (crucial for concurrency).
      - **NoSQL (Optional/Supplement):** MongoDB for certain data, or Redis for caching/queues. You can use a hybrid approach later.
    - **Authentication:** JWT (JSON Web Tokens) for stateless authentication.
    - **Testing:** Jest/Mocha (Node.js), Pytest (Python), JUnit (Java), etc.
    - **Documentation:** OpenAPI (Swagger).
    - **Containerization:** Docker.

3.  **Database Schema Design:**

    - **Key Entities and Relationships:**
      - `User`: id, username, email, password_hash, role (attendee, organizer).
      - `Event`: id, organizerId (FK to User), name, description, date, location, totalCapacity, status (upcoming, sold_out, cancelled, past).
      - `TicketType`: id, eventId (FK to Event), name (e.g., "Standard", "VIP"), price, quantityAvailable, quantitySold.
      - `Booking`: id, userId (FK to User), eventId (FK to Event), bookingDate, totalPrice, status (pending, confirmed, cancelled).
      - `BookingItem`: id, bookingId (FK to Booking), ticketTypeId (FK to TicketType), quantity, priceAtBooking.
    - **Diagram:** Draw an ERD (Entity-Relationship Diagram). Tools like draw.io or Lucidchart can help.

4.  **Project Setup & Version Control:**
    - Initialize Git repository.
    - Set up your project structure (e.g., `src/controllers`, `src/services`, `src/models`, `src/routes`).
    - Install initial dependencies.
    - Set up environment variables (`.env` for database credentials, JWT secret, etc.).
    - Configure a linter and formatter (e.g., ESLint/Prettier for JS, Black/Flake8/Ruff for Python).

---

### Phase 1: Basic CRUD & User Management

**Learning Objectives:**

- **API Design:** Implementing RESTful endpoints.
- **Database Interactions:** Performing basic CRUD operations.
- **Authentication:** Implementing user registration and login with secure password handling.
- **Routing & Controllers:** Mapping HTTP requests to business logic.
- **Input Validation:** Protecting your API from malformed data.

**Steps:**

1.  **User Authentication & Authorization:**
    - Implement user registration (`POST /api/auth/register`).
    - Implement user login (`POST /api/auth/login`).
    - Securely hash passwords (e.g., bcrypt, Argon2).
    - Generate and verify JWTs.
    - Create middleware (or decorators/guards) for authenticating requests and authorizing based on roles (attendee/organizer).
2.  **Event Management (Organizer Features):**
    - **Event CRUD:** `POST /api/events` (create), `GET /api/events` (list all/filter), `GET /api/events/:id` (get one), `PUT /api/events/:id` (update), `DELETE /api/events/:id` (delete).
    - Ensure only the _organizer_ of an event can update/delete it.
3.  **Ticket Type Management (Organizer Features):**
    - `POST /api/events/:eventId/ticket-types` (create ticket type for an event).
    - `GET /api/events/:eventId/ticket-types` (list ticket types).
    - Implement logic to update `quantityAvailable` when tickets are sold or cancelled.
4.  **Public Event Browse:**
    - `GET /api/events` (public endpoint to list active/upcoming events).
    - `GET /api/events/:id` (public endpoint to view event details).
    - Implement search and basic filtering (by date, location, event name).

---

### Phase 2: Booking & Concurrency Handling (The Core Challenge!)

**Learning Objectives:**

- **Transactions:** Ensuring atomicity of operations.
- **Concurrency Control:** Preventing race conditions and overbooking.
- **Complex Business Logic:** Orchestrating multiple database operations.
- **Error Handling:** More sophisticated error responses for business logic failures.

**Steps:**

1.  **Ticket Availability & Booking Logic:**

    - **Booking Endpoint:** `POST /api/bookings` (user selects eventId, ticketTypeId, quantity).
    - **Critical Section:** This is where concurrency is key.
      - Check if requested `quantity` is available for the `ticketType`.
      - **Crucially:** Decrement `quantityAvailable` and increment `quantitySold` for the `TicketType`.
      - Create a `Booking` record.
      - Create `BookingItem` records for each ticket.
    - **Transaction Management:** Wrap all these operations in a database transaction. If any step fails (e.g., not enough tickets, database error), roll back the entire transaction. This prevents partial updates and ensures data integrity.
      - _(For SQL databases: `BEGIN TRANSACTION; ... COMMIT;` or `ROLLBACK;`)_
      - _(For NoSQL databases like MongoDB: Replica sets support multi-document transactions.)_
    - **Concurrency Strategy (Choose one initially, or discuss alternatives):**
      - **Pessimistic Locking:** Lock the `TicketType` record (or specific row) before checking and updating. Release the lock after the transaction. (Common for SQL dbs, e.g., `SELECT ... FOR UPDATE` in PostgreSQL/MySQL).
      - **Optimistic Locking:** Add a `version` or `updatedAt` field to `TicketType`. When updating, check that the `version` hasn't changed since you last read it. If it has, retry the operation. (More common for higher throughput in distributed systems, requires client-side retry logic).
      - **Database Constraints:** Use unique constraints where appropriate (e.g., a user can only book a specific ticket type once per booking, or total capacity validation at DB level).
    - **Temporary Holds (Optional, but good for real-world):** Implement a mechanism to temporarily hold tickets for a short period (e.g., 5-10 minutes) while a user is completing a purchase. If the purchase isn't completed, release the tickets. This adds complexity with background jobs.

2.  **User Order History:**

    - `GET /api/users/:userId/bookings` (for attendees to see their past and current bookings).
    - `GET /api/bookings/:id` (details of a specific booking).

3.  **Booking Cancellation:**
    - `PUT /api/bookings/:id/cancel` (user cancels their own booking).
    - Logic to increment `quantityAvailable` and decrement `quantitySold` for the associated `TicketType`.
    - Transaction required here as well.
    - Consider a refund process (mocked).

---

### Phase 3: Enhancements & Polish (The Portfolio Shine)

**Learning Objectives:**

- **Advanced Querying:** Implementing effective search, filtering, and pagination.
- **Caching:** Improving API performance.
- **Asynchronous Processing:** Handling background tasks.
- **Containerization:** Deploying your application with Docker.
- **API Documentation:** Making your API consumable.
- **Testing Best Practices:** Comprehensive testing.

**Steps:**

1.  **Advanced Filtering, Search, & Pagination:**
    - Implement robust filtering on `GET /api/events` (by date range, location, category, price range, availability).
    - Add keyword search.
    - Implement pagination (`?page=1&limit=10`).
    - Add sorting options (`?sortBy=date&order=asc`).
2.  **Caching (Redis):**
    - Cache frequently accessed data, like event listings (`GET /api/events`).
    - Implement cache invalidation strategies (e.g., when events are created/updated/deleted or when ticket availability changes).
3.  **Asynchronous Tasks (Using a Message Queue - e.g., RabbitMQ, Redis Streams/BullMQ/Celery):**
    - **Booking Confirmation Emails:** Instead of sending an email directly in the booking transaction (which is slow and error-prone), push a message to a queue. A separate worker process consumes the message and sends the email.
    - **Reporting:** Generate daily/weekly booking reports for organizers in the background.
    - **Why:** Improves API response time, makes the system more resilient to external service failures, and allows for scalable background processing.
4.  **API Documentation (OpenAPI/Swagger):**
    - Integrate a tool like Swagger UI (e.g., `swagger-ui-express` for Node.js, `drf-yasg` or `drf-spectacular` for Python).
    - Document all endpoints, request/response schemas, authentication requirements, and error codes.
5.  **Comprehensive Testing:**
    - **Unit Tests:** For all your controllers, services, and utility functions.
    - **Integration Tests:** Test interactions between services and the database (e.g., successful booking flow, handling overbooking).
    - **API/End-to-End Tests:** Use a tool (e.g., Postman/Newman, Supertest) to test your API endpoints. Test various scenarios, including valid requests, invalid inputs, unauthorized access, and concurrency attempts.
6.  **Dockerization:**
    - Create a `Dockerfile` for your API.
    - Create a `docker-compose.yml` to spin up your API, database, and Redis/message queue with a single command. This makes your project incredibly easy for others to run.
7.  **Advanced Error Handling & Logging:**
    - Implement a centralized error handling mechanism (middleware, global exception handler).
    - Use a proper logging library to log requests, errors, and critical business events.
    - Return clear, standardized API error responses with appropriate HTTP status codes.

---

### Phase 4: Deployment & Future Considerations (Production Readiness)

**Learning Objectives:**

- **Deployment:** Getting your API live.
- **Cloud Concepts:** Understanding basic cloud infrastructure.
- **Scalability:** Thinking about how your application would handle more users.
- **Security Best Practices:** Beyond just auth.
- **Compliance:** Basic awareness for the EU market.

**Steps:**

1.  **Deployment:**
    - Choose a cloud platform (e.g., Heroku, Railway, Render for simplicity; AWS EC2/Lightsail, Google Cloud Run/App Engine for more control).
    - Provide clear deployment instructions in your `README.md`.
    - Consider setting up a simple CI/CD pipeline (GitHub Actions) to automatically run tests and potentially deploy on push.
2.  **Security Review:**
    - **Environment Variables:** Ensure all sensitive data is stored securely.
    - **Rate Limiting:** Protect against brute-force attacks or API abuse.
    - **CORS:** Properly configure Cross-Origin Resource Sharing.
    - **Dependency Security:** Keep dependencies updated, use tools for vulnerability scanning.
3.  **Performance Optimization:**
    - Review database query performance (explain plans).
    - Add appropriate indexes to your database tables.
4.  **README.md & GitHub Profile:**
    - **Project Title & Description:** Catchy and informative.
    - **Tech Stack:** Clearly list everything used.
    - **Features:** Bullet points of what your API can do.
    - **Getting Started:** Clear installation, setup, and running instructions (local and Docker).
    - **API Endpoints:** Link to your live Swagger UI (if deployed).
    - **Architectural Overview:** A simple diagram showing components.
    - **Concurrency Strategy:** Explain _how_ you handled concurrency and why you chose that method.
    - **Asynchronous Processing:** Detail how asynchronous tasks are used.
    - **Future Improvements/Roadmap:** Show you've thought beyond the current state.
    - **Contact Info:** Your name, LinkedIn, GitHub.
    - **GDPR/Privacy (for EU):** Briefly mention how you'd approach data privacy (e.g., data minimization, data retention policies) if this were a production system, even if not fully implemented in the demo.
