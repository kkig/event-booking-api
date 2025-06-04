# API Endpoints Names
PASSWORD_RESET_CONFIRM_NAME = "accounts:password_reset_confirm"


class PasswordMessasges:
    INVALID_UID_OR_NO_USER = "Invalid user ID or user does not exist."
    RESET_LINK_EXPIRED = "The reset link is invalid or has expired."
    RESET_CONFIRM = "Password has been reset successfully."
    NOT_MATCH = "New passwords do not match."


# Email
PASSWORD_RESET_SUBJECT = "Password Reset Request"
PASSWORD_RESET_MESSAGE = (
    "If an account with that email exists, a password reset email has been sent."
)
