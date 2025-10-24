from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import KeyValue
from .serializers import KeyValueSerializer, KeyValueUpsertSerializer


class KeyValueViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = KeyValue.objects.all()
    permission_classes = [IsAuthenticated]

    lookup_field = "key"
    lookup_url_kwarg = "key"
    lookup_value_regex = r"[^/]+"

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return KeyValueUpsertSerializer
        return KeyValueSerializer

    def update(self, request, *args, **kwargs):
        key = kwargs.get(self.lookup_url_kwarg)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj, created = KeyValue.objects.update_or_create(
            key=key, defaults={"value": serializer.validated_data["value"]}
        )
        out = KeyValueSerializer(obj)
        return Response(
            out.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
