from django.contrib.auth.password_validation import BaseValidator
from django.core.exceptions import ValidationError

class CustomPasswordValidator(BaseValidator):
    def validate(self, password, user=None):
        # Check if the password is too similar to other personal information
        if password.lower() in [user.username.lower(), user.email.lower()]:
            raise ValidationError("Your password is too similar to your username or email.")
        
        # Check if the password meets the minimum length requirement
        if len(password) < 8:
            raise ValidationError("Your password must contain at least 8 characters.")
        
        # Check if the password is a commonly used password
        common_passwords = ["password", "123456", "qwerty"]  # Add more common passwords as needed
        if password.lower() in common_passwords:
            raise ValidationError("Your password is too common and easy to guess.")

    def get_help_text(self):
        return "Your custom help text here"
