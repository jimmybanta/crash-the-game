''' Utility functions for reading and writing S3 files. '''

import os
import boto3

def aws_session():
    '''
    Returns an AWS session.
    '''

    return boto3.Session()

def aws_client(service, session=None):
    '''
    Returns an AWS client.
    '''

    if not session:
        session = aws_session()

    return session.client(service)

def read_object(bucket, key, client=None):
    '''
    Reads an object from S3, returns binary data.
    '''

    if not client:
        client = aws_client('s3')

    return client.get_object(Bucket=bucket, Key=key)['Body'].read()

def write_object(bucket_name, key, data, client=None):
    '''Given binary data, writes to s3.'''

    if not client:
        client = aws_client('s3')

    return client.put_object(Bucket=bucket_name, Key=key, Body=data)
    
    
def list_objects(bucket, prefix='', client=None):
    '''
    Lists objects in an S3 bucket.
    '''

    if not client:
        client = aws_client('s3')

    # get the objects
    # if it returns a key error, then the given prefix doesn't exist
    try:
        objects =  client.list_objects(Bucket=bucket, Prefix=prefix)['Contents']
    except KeyError:
        return []

    # if there's only one object, and it's the directory, it will return it
    # but we don't count that as a file
    if len(objects) == 1 and objects[0]['Key'] == prefix or objects[0]['Key'] == f'{prefix}/':
        return []
    
    # remove the prefix from each item
    return [os.path.basename(obj['Key']) for obj in objects]

def check_object_exists(bucket, key, client=None):
    '''
    Checks if an object exists in an S3 bucket.
    '''

    if not client:
        client = aws_client('s3')

    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False