from .models import custom_user

def user_progress(request):
    if request.user.is_authenticated:
        try:
            CustomUser = custom_user.objects.get(user=request.user)
            CustomUser.update_progress()
            return {
                'custom_user': CustomUser,
                'level': CustomUser.level,
                'rank': CustomUser.rank,
                'exp_required': CustomUser.get_exp_per_level(),
                'exp_earned': CustomUser.get_current_level_exp_total(),
            }
        except custom_user.DoesNotExist:
            pass
    return {}