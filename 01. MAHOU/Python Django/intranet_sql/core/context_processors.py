def admin_flag(request):
    user = request.user
    if not user.is_authenticated:
        return {"is_admin": False}

    return {
        "is_admin": (
            user.is_staff or user.groups.filter(name="Admin").exists()
        )
    }
