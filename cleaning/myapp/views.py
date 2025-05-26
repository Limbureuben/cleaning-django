import graphene
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token, create_refresh_token
from graphene_django.types import DjangoObjectType

User = get_user_model()

# UserType
class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('password',)

# Registration mutation
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password_confirm = graphene.String(required=True)

    def mutate(self, info, username, email, password, password_confirm):
        if password != password_confirm:
            return RegisterUser(
                success=False,
                message="Passwords do not match."
            )

        if User.objects.filter(username=username).exists():
            return RegisterUser(
                success=False,
                message="User with this username already exists."
            )

        user = User(username=username, email=email, is_staff=False)
        user.set_password(password)
        user.save()

        token = get_token(user)

        return RegisterUser(
            user=user,
            token=token,
            message="User registered successfully.",
            success=True
        )

# Login mutation
class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
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
        refresh_token = create_refresh_token(user)

        return LoginUser(
            user=user,
            token=token,
            refresh_token=refresh_token,
            message="Login successful.",
            success=True
        )


class HelloQuery(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stanger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"