''' Utility functions for reading and writing S3 files. '''

import os
import boto3

from games.decorators import retry_on_exception


@retry_on_exception(max_retries=3, delay=2)
def aws_session():
    '''
    Generates an AWS session.

    Returns
    -------
    boto3.Session
    '''

    return boto3.Session()

@retry_on_exception(max_retries=3, delay=2)
def aws_client(service, session=None):
    '''
    Returns an AWS client.

    Parameters
    ----------
    service : str
        The AWS service to use.
    session : boto3.Session | None
        The session to use. If None, then a new session is created.
    '''

    if not session:
        session = aws_session()

    return session.client(service)

@retry_on_exception(max_retries=3, delay=2)
def read_object(bucket, key, client=None):
    '''
    Reads an object from S3.

    Parameters
    ----------
    bucket : str
        The name of the bucket.
    key : str
        The key of the object.
    client : boto3.client | None
        The client to use. If None, then a new client is created.

    Returns
    -------
    bytes 
        The binary data of the file
    '''

    if not client:
        client = aws_client('s3')

    return client.get_object(Bucket=bucket, Key=key)['Body'].read()

@retry_on_exception(max_retries=3, delay=2)
def write_object(bucket_name, key, data, client=None):
    '''Writes an object to s3.
    
    Parameters
    ----------
    bucket_name : str
        The name of the bucket.
    key : str
        The key of the object.
    data : bytes
        The data to write.
    client : boto3.client | None
        The client to use. If None, then a new client is created.

    Returns
    -------
    None
    '''

    if not client:
        client = aws_client('s3')

    client.put_object(Bucket=bucket_name, Key=key, Body=data)
    
@retry_on_exception(max_retries=3, delay=2)
def list_objects(bucket, prefix='', client=None):
    '''
    Lists objects in an S3 bucket.

    Parameters
    ----------
    bucket : str
        The name of the bucket.
    prefix : str | ''
        The prefix to search for.
    client : boto3.client | None
        The client to use. If None, then a new client is created.
    
    Returns
    -------
    list
        A list of the objects in the bucket.
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

@retry_on_exception(max_retries=3, delay=2)
def check_object_exists(bucket, key, client=None):
    '''
    Checks if an object exists in an S3 bucket.

    Parameters
    ----------
    bucket : str
        The name of the bucket.
    key : str
        The key of the object.
    client : boto3.client | None
        The client to use. If None, then a new client is created.

    Returns
    -------
    bool
        Whether the object exists.
    '''

    if not client:
        client = aws_client('s3')

    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False