from icg import play, card
from icg.proto import cardpool_pb2
import uuid
import os
import time
import base64

import boto3
dynamodb = boto3.resource('dynamodb')


def new_card_pool(event, context):
    pool = card.generate_pool()
    new_id = str(uuid.uuid1())
    print(new_id)
    protoPool = card.pool_to_proto(pool, id=new_id)
    poolSerialized = protoPool.SerializeToString()

    timestamp = int(time.time() * 1000)

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'id': new_id,
        'data': poolSerialized,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # write the todo to the database
    table.put_item(Item=item)

    # create a response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/x-protobuf'
        },
        'isBase64Encoded': True,
        # we are base64 encoding and then converting those bytes to a string object with .decode()
        'body': base64.b64encode(poolSerialized).decode()
    }

    return response


def get(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )

    protoPool = cardpool_pb2.CardPool()
    protoPool.ParseFromString(result['Item']['data'].data)

    # create a response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/x-protobuf'
        },
        # we are base64 encoding and then converting those bytes to a string object with .decode()
        'body': base64.b64encode(result['Item']).decode()
    }

    return response


def submit_deck(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )

    protoPool = cardpool_pb2.CardPool()
    protoPool.ParseFromString(result['Item']['data'])

    cardPool = card.pool_from_proto(protoPool)
    data = event['body']
    deck = cardpool_pb2.Deck()
    deck.ParseFromString(data)
    print(str(deck.card_ids))

    deckResult = play.play(deck, cardPool)

    # create a response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/x-protobuf'
        },
        'isBase64Encoded': True,
        # we are base64 encoding and then converting those bytes to a string object with .decode()
        'body': base64.b64encode(deckResult.SerializeToString()).decode()
    }

    return response
