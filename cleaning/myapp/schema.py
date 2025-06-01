import graphene
from .views import *

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()

class Query(HelloQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)