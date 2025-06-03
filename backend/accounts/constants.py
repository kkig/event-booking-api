# Password Reset
class NewPasswords:
    ONE = "new_password1"
    TWO = "new_password2"
    NOT_MATCH = "New passwords do not match."


# Password Reset Confirmation
class PasswordMessasges:
    INVALID_UID_OR_NO_USER = "Invalid user ID or user does not exist."
    RESET_LINK_EXPIRED = "The reset link is invalid or has expired."
    RESET_CONFIRM = "Password has been reset successfully."


# Email
PASSWORD_RESET_SUBJECT = "Password Reset Request"
PASSWORD_RESET_MESSAGE = (
    "If an account with that email exists, a password reset email has been sent."
)
