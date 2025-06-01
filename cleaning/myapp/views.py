import graphene # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from graphql_jwt.utils import get_token # type: ignore
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "is_staff", "is_superuser")

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        role = graphene.String(required=False)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, password, confirm_password, role=None):
        if password != confirm_password:
            return RegisterUser(success=False, message="Passwords do not match")

        if User.objects.filter(username=username).exists():
            return RegisterUser(success=False, message="Username already exists")

        user = User(username=username)
        
        if role == 'staff':
            user.is_staff = True
            user.is_superuser = False  # You could also set True if needed
        else:
            user.is_staff = False
            user.is_superuser = False

        user.set_password(password)
        user.save()

        return RegisterUser(user=user, success=True, message="User registered successfully")


# Login mutation
class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return LoginUser(
                success=False,
                message="Invalid username or password."
            )

        token = get_token(user)

        return LoginUser(
            user=user,
            token=token,
            message="Login successful.",
            success=True
        )


class HelloQuery(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stanger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"