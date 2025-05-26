import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stanger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"

schema = graphene.Schema(query=Query)