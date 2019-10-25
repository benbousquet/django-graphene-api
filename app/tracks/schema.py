import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Track, Like
from users.schema import UserType


# make the track type
class TrackType(DjangoObjectType):
    # model it after the track model
    class Meta:
        model = Track


# make the like type
class LikeType(DjangoObjectType):
    # model it after the like model
    class Meta:
        model = Like


# create the query type
class Query(graphene.ObjectType):

    tracks = graphene.List(TrackType, search=graphene.String())
    likes = graphene.List(LikeType)

    # resolve the tracks query
    def resolve_tracks(self, info, search=None):
        if search:
            return Track.objects.filter(title__contains=search)

        return Track.objects.all()

    # resolve the likes query
    def resolve_likes(self, info):
        return Like.objects.all()


# create mutation to create a track
class CreateTrack(graphene.Mutation):
    # define the output
    track = graphene.Field(TrackType)

    # define the arguments that the mutation will accept
    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    # mutation
    def mutate(self, info, title, description, url):
        # gets user from header
        user = info.context.user
        # if not logged in raise an error
        if user.is_anonymous:
            raise GraphQLError('Log in to add a track')

        # creates a new track and save it to the db
        track = Track(title=title, description=description, url=url, posted_by=user)
        track.save()
        # pass in output
        return CreateTrack(track=track)


# create mutation that updates a track
class UpdateTrack(graphene.Mutation):
    # define the output
    track = graphene.Field(TrackType)

    # define the arguments that the mutation will accept
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    # mutation
    def mutate(self, info, track_id, title, url, description):
        # gets user from header
        user = info.context.user
        # get the track from the db
        track = Track.objects.get(id=track_id)

        # check if the post was posted_by the user
        if track.posted_by != user:
            raise GraphQLError('Not permitted to update this track')

        # update the values on track
        track.title = title
        track.description = description
        track.url = url
        # save the track to the db
        track.save()
        # return the updated track to the user
        return UpdateTrack(track=track)


# create mutation to delete a track
class DeleteTrack(graphene.Mutation):
    # define the output
    track_id = graphene.Int()

    # define the arguments that the mutation will accept
    class Arguments:
        track_id = graphene.Int()

    # mutation
    def mutate(self, info, track_id):
        # gets user from header
        user = info.context.user
        # get a track with passed in id
        track = Track.objects.get(id=track_id)

        # checks if the user is logged in
        if track.posted_by != user:
            raise GraphQLError('Not permitted to delete this track')

        # delete track
        track.delete()

        # return the deleted track id to the user
        return DeleteTrack(track_id=track_id)


# create mutation to create a like
class CreateLike(graphene.Mutation):
    # define the output
    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    # define the arguments that the mutation will accept
    class Arguments:
        track_id = graphene.Int(required=True)

    # mutation
    def mutate(self, info, track_id):
        # gets user from header
        user = info.context.user
        # checks if the user is logged in
        if user.is_anonymous:
            raise GraphQLError('Login to like tracks')

        # get a track with id
        track = Track.objects.get(id=track_id)
        # if a track doesnt exist raise an error
        if not track:
            raise GraphQLError('Cannot find track with given track id')
        # create a like object with user and track
        Like.objects.create(
            user=user,
            track=track
        )
        # return created like
        return CreateLike(user=user, track=track)

# creates the mutation type
class Mutation(graphene.ObjectType):
    # add mutations as fields to mutation
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    create_like = CreateLike.Field()
