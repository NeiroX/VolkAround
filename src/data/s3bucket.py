import os
import boto3
import logging
from urllib.parse import urlparse
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from io import BytesIO
from src.settings import AWS_REGION, AWS_SERVER_PUBLIC_KEY, AWS_SERVER_SECRET_KEY, BUCKET_NAME, ENDPOINT_URL, \
    CUSTOM_ENDPOINT_URL, EDGE_ENDPOINT_URL


def get_s3_client() -> BaseClient:
    session = boto3.session.Session()
    return session.client('s3',
                          region_name=AWS_REGION,
                          endpoint_url=ENDPOINT_URL,
                          aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
                          aws_secret_access_key=AWS_SERVER_SECRET_KEY)


def save_file_to_s3(file_path: str, s3_file_name: str, s3_directory: str = "images/") -> str | None:
    """
    Uploads a photo to an AWS S3 bucket.

    :param s3_file_name:
    :param file_path: The local file path of the photo to upload.
    :param s3_directory: The directory in the S3 bucket where the photo will be stored. Default is "images/".
    :return: The public URL of the uploaded photo if successful, None otherwise.
    """
    # Ensure the file exists locally
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Photo not found: {file_path}")

    # Extract the file name and generate the S3 object key
    s3_object_key = os.path.join(s3_directory, s3_file_name)

    # Determine the MIME type of the file
    # mime_type, _ = mimetypes.guess_type(file_path)

    try:
        # Upload the file to S3
        s3_client = get_s3_client()  # Assume get_s3_client() is defined to return a configured S3 client

        s3_client.upload_file(file_path, BUCKET_NAME, s3_object_key)

        # Generate the public URL of the uploaded photo
        photo_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_object_key}"
        return photo_url

    except ClientError as e:
        logging.error(f"Failed to upload photo to S3: {e}")
        return None


def s3_file_exists(file_url) -> bool:
    """Check if a file exists in the S3 bucket using its URL."""
    try:
        parsed_url = urlparse(file_url)
        file_key = parsed_url.path.lstrip('/')  # Extract the file key from the URL

        s3_client = get_s3_client()
        s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        logging.error(f"Error checking file existence in S3: {e}")
        return False


def s3_fetch_file(file_url) -> BytesIO | None:
    """Fetch a file from S3 using its URL."""
    try:
        parsed_url = urlparse(file_url)
        file_key = parsed_url.path.lstrip('/')  # Extract the file key from the URL

        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        return BytesIO(response['Body'].read())
    except ClientError as e:
        logging.error(f"Failed to fetch file from S3: {e}")
        return None


def s3_delete_file(file_url) -> bool:
    """Delete a file from S3 bucket using its URL."""
    try:
        parsed_url = urlparse(file_url)
        file_key = parsed_url.path.lstrip('/')  # Extract the file key from the URL

        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        logging.info(f"File deleted from S3: {file_key}")
        return True
    except ClientError as e:
        logging.error(f"Failed to delete file from S3: {e}")
        return False
