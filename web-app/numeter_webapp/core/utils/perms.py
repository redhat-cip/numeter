from core.models import Group, Host


def has_perm(user, model_class, model_id):
    if user.is_superuser:
        return True
    else:
        if model_class == Group:
            return user.groups.filter(id=model_id).exists()
        elif model_class == Host:
            group = Host.objects.get(id=model_id).group
            if group:
                return user.groups.filter(id=group.id).exists()
            else:
                return False
