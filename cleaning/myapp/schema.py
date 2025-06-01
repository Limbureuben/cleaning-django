import graphene
from .views import *

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()

class Query(HelloQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)