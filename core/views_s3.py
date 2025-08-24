import uuid, datetime, re, os
import boto3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import json

# boto3 client
s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def _safe_name(name: str) -> str:
    return re.sub(r"\s+", "_", name)

@require_GET
def presign_put(request):
    filename = request.GET.get("filename")
    content_type = request.GET.get("contentType") or "application/octet-stream"

    if not filename:
        return JsonResponse({"error": "filename required"}, status=400)

    key = f"profile/{datetime.date.today()}/{uuid.uuid4()}_{_safe_name(filename)}"

    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,  # 5분
    )

    object_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

    return JsonResponse({"url": url, "key": key, "objectUrl": object_url})

@require_POST
def presign_get(request):
    """비공개 버킷일 때 이미지 표시용 presigned GET"""
    body = json.loads(request.body or "{}")
    key = body.get("key")
    if not key:
        return JsonResponse({"error": "key required"}, status=400)

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
        ExpiresIn=300,
    )
    return JsonResponse({"url": url})