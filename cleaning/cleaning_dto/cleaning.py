import graphene

class RegistrationObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()

class RegistrationInputObject(graphene.InputObjectType):
    username = graphene.String()
    email = graphene.String(required=False)
    password = graphene.String()
    passwordConfirm = graphene.String()
    role = graphene.String(required=False)
    sessionId = graphene.String(required=False)
    ward = graphene.String()

class RegisterObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()