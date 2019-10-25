import graphene
import tracks.schema
import users.schema
import graphql_jwt


# pass all queries into schema
class Query(users.schema.Query, tracks.schema.Query, graphene.ObjectType):
    pass


# pass all mutations into schema
class Mutation(users.schema.Mutation, tracks.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


# define the schema and pass in the queries and mutations
schema = graphene.Schema(query=Query, mutation=Mutation)
