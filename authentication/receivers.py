def new_user(sender, **kwargs):
    user = kwargs.get('instance')
    print(f"The user {user} has been registered.")