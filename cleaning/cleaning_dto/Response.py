import graphene
from .cleaning import *


class RegistrationResponse(graphene.ObjectType):
    message = graphene.String()
    success = graphene.Boolean()
    user = graphene.Field(RegisterObject)

class RegisterObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()