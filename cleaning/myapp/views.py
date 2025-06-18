import graphene # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from graphene_django.types import DjangoObjectType # type: ignore
from django.contrib.auth.models import User
from graphql_jwt.shortcuts import get_token # type: ignore
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from graphene_django import DjangoObjectType
from cleaning_dto.cleaning import *
from cleaning_dto.Response import *
from cleaningBuilders.cleaningBuilder import *


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "is_staff", "is_superuser")


class RegistrationMutation(graphene.Mutation):
    user = graphene.Field(RegistrationObject)
    output = graphene.Field(RegistrationResponse)

    class Arguments:
        input = RegistrationInputObject(required=True)

    def mutate(self, info, input):
        response = register_user(input)
        return RegistrationMutation(user=response.user, output=response)


class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserLoginObject)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, password):
        try:
            user = authenticate(username=username, password=password)

            if user is None:
                return LoginUser(success=False, message="Invalid credentials")
            
            if not isinstance(user, CustomUser):
                raise ValidationError("User is not a valid CustomUser instance.")

            # Create JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = UserLoginObject(
                id=user.id,
                username=user.username,
                token=access_token,
                isStaff=user.is_staff,
                isCleaner=(user.role == "is_cleaner")
            )

            return LoginUser(
                user=user_data,
                success=True,
                message=f"{user.role} login successful"
            )

        except Exception as e:
            return LoginUser(success=False, message=f"An error occurred: {str(e)}")


# class LoginUser(graphene.Mutation):
#     user = graphene.Field(lambda: UserType)
#     token = graphene.String()
#     message = graphene.String()
#     success = graphene.Boolean()

#     class Arguments:
#         username = graphene.String(required=True)
#         password = graphene.String(required=True)

#     def mutate(self, info, username, password):
#         user = authenticate(username=username, password=password)

#         if user is None:
#             return LoginUser(
#                 success=False,
#                 message="Invalid username or password."
#             )

#         # token = get_token(user)
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)

#         return LoginUser(
#             user=user,
#             # token=token,
#             token=access_token,
#             message="Login successful.",
#             success=True
#         )


class HelloQuery(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stanger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"