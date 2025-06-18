import graphene
from .Response import *

class RegistrationResponse(graphene.ObjectType):
    message = graphene.String()
    success = graphene.Boolean()
    user = graphene.Field(RegisterObject) 