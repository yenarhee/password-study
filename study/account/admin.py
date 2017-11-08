from django.contrib import admin

from .models import (UserProfile, UserProfileAdmin, LoginAttempt, LoginAttemptAdmin,
                     PasswordRequest, PasswordRequestAdmin, EmailVerification, EmailVerificationAdmin,
                     Feedback, FeedbackAdmin)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)
admin.site.register(PasswordRequest, PasswordRequestAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(Feedback, FeedbackAdmin)
