import graphene
from .views import *

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stanger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"

schema = graphene.Schema(query=Query, mutation=Mutation)