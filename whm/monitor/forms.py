from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# Form for creating new users in the Django Admin
class CustomUserCreationForm(UserCreationForm):
    """
    Minimal UserCreationForm tailored for the CustomUser model.
    Inherits default behavior from Django's UserCreationForm.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Explicitly list the fields needed for user creation in the Admin
        fields = ('email', 'mobile_number', 'first_name', 'last_name')


# Form for changing existing user data in the Django Admin
class CustomUserChangeForm(UserChangeForm):
    """
    Minimal UserChangeForm tailored for the CustomUser model.
    Inherits default behavior from Django's UserChangeForm.
    """
    class Meta:
        model = CustomUser
        # Using '__all__' is the simplest way to include all editable fields for the change view.
        fields = '__all__'
