def new_user(sender, **kwargs):
    print(f"The user {kwargs.get('username')} has been registered.")