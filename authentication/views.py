from django import shortcuts, db, http, urls
from django.contrib import auth, messages
from . import models as auth_models, serializers as auth_serializers
from rest_framework import generics, views, permissions, response, exceptions


# App views

def index(request):
    return shortcuts.redirect('login')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            auth.login(request, user)
            return http.HttpResponseRedirect(urls.reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return shortcuts.render(request, "authentication/login.html")
    else:
        return shortcuts.render(request, "authentication/login.html")


def logout_view(request):
    auth.logout(request)
    return shortcuts.HttpResponseRedirect(urls.reverse("index"))


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return shortcuts.render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = auth_models.User.objects.create_user(name, username, email, password)
            user.save()
        except db.IntegrityError:
            messages.error(request, "Username already taken.")
            return shortcuts.render(request, "auctions/register.html")
        auth.login(request, user)
        return shortcuts.HttpResponseRedirect(urls.reverse("index"))
    else:
        return shortcuts.render(request, "authentication/register.html")
    
    
# API endpoints

class RegisterAPIView(generics.CreateAPIView):
    queryset = auth_models.User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = auth_serializers.RegistrationSerializer
    
register_api_view = RegisterAPIView.as_view()


class LoginAPIView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return response.Response(request.data, status=200)
        raise exceptions.ValidationError({"error": "Invalid credentials."}, code=400)
    
login_api_view = LoginAPIView.as_view()


class LogoutAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        auth.logout(request)
        return response.Response(status=200)
    
logout_api_view = LogoutAPIView.as_view()