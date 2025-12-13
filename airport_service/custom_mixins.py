import logging
import hashlib

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from django.core.cache import cache
from rest_framework.response import Response


logger = logging.getLogger(__name__)


def cached_detail(viewset, request, *args, **kwargs):
    """
    Cached detail for heavy queries.
    Key format: <cache_key_prefix>_<pk>.
    """

    pk = kwargs.get("pk")
    if not pk:
        return super(viewset.__class__, viewset).retrieve(  # noqa
            request, *args, **kwargs
        )

    key = f"{viewset.cache_key_prefix}_{pk}"
    cached = cache.get(key)

    if cached:
        logger.info(f"👍 Redis: returning cached detail {key}")
        return Response(cached)

    parent = super(viewset.__class__, viewset)
    response = parent.retrieve(request, *args, **kwargs)  # noqa

    cache.set(key, response.data, timeout=10)
    return response


class AdminOrReadOnly(viewsets.ModelViewSet):
    """
    Allow read-only access for unauthenticated users,
     full access for admins.
    """

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]


class RedisListCacheMixin:
    cache_key = None
    cache_timeout = 60

    def list(self, request, *args, **kwargs):
        if not self.cache_key:
            return super().list(request, *args, **kwargs)

        cached = cache.get(self.cache_key)
        if cached:
            logger.info(f"👍 Redis LIST: returning cached {self.cache_key}")
            return Response(cached)

        response = super().list(request, *args, **kwargs)

        cache.set(self.cache_key, response.data, timeout=self.cache_timeout)
        logger.info(f"✨ Cached LIST result under key: {self.cache_key}")

        return response

    def _delete_all_param_keys(self):
        cache.delete(self.cache_key)

    def perform_create(self, serializer):
        obj = serializer.save()
        self._delete_all_param_keys()
        return obj

    def perform_update(self, serializer):
        obj = serializer.save()
        self._delete_all_param_keys()
        return obj

    def perform_destroy(self, instance):
        self._delete_all_param_keys()
        return super().perform_destroy(instance)
