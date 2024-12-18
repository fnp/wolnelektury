from rest_framework.pagination import LimitOffsetPagination, PageLink
from rest_framework.response import Response


class WLLimitOffsetPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            "member": data,
            "totalItems": self.count,
            "view": {
                "previous": self.get_previous_link(),
                "next": self.get_next_link(),
            }
        })
