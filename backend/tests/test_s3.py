import pytest
from games.s3 import list_objects, aws_client

@pytest.fixture
def mock_aws_client(mocker):
    mock_client = mocker.Mock()
    mocker.patch('games.s3.aws_client', return_value=mock_client)
    return mock_client

def test_list_objects_no_client(mocker, mock_aws_client):
    mock_list_objects = mock_aws_client.list_objects
    mock_list_objects.return_value = {'Contents': [{'Key': 'prefix/file1.txt'}, {'Key': 'prefix/file2.txt'}]}
    
    bucket = 'dummy_bucket'
    prefix = 'prefix'
    result = list_objects(bucket, prefix)
    
    assert result == ['file1.txt', 'file2.txt']
    mock_list_objects.assert_called_once_with(Bucket=bucket, Prefix=prefix)

def test_list_objects_with_client(mocker):
    mock_client = mocker.Mock()
    mock_list_objects = mock_client.list_objects
    mock_list_objects.return_value = {'Contents': [{'Key': 'prefix/file1.txt'}, {'Key': 'prefix/file2.txt'}]}
    
    bucket = 'dummy_bucket'
    prefix = 'prefix'
    result = list_objects(bucket, prefix, client=mock_client)
    
    assert result == ['file1.txt', 'file2.txt']
    mock_list_objects.assert_called_once_with(Bucket=bucket, Prefix=prefix)

def test_list_objects_empty_prefix(mocker, mock_aws_client):
    mock_list_objects = mock_aws_client.list_objects
    mock_list_objects.return_value = {'Contents': [{'Key': 'prefix/'}]}
    
    bucket = 'dummy_bucket'
    prefix = 'prefix'
    result = list_objects(bucket, prefix)
    
    assert result == []
    mock_list_objects.assert_called_once_with(Bucket=bucket, Prefix=prefix)

def test_list_objects_key_error(mocker, mock_aws_client):
    mock_list_objects = mock_aws_client.list_objects
    mock_list_objects.side_effect = KeyError
    
    bucket = 'dummy_bucket'
    prefix = 'prefix'
    result = list_objects(bucket, prefix)
    
    assert result == []
    mock_list_objects.assert_called_once_with(Bucket=bucket, Prefix=prefix)