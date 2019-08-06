# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from django.http import Http404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from picture.forms import PictureImportForm
from picture.models import Picture


class PicturesView(APIView):
    permission_classes = [DjangoModelPermissions]
    queryset = Picture.objects.none()  # Required for DjangoModelPermissions

    def post(self, request):
        data = json.loads(request.POST.get('data'))
        form = PictureImportForm(data)
        if form.is_valid():
            form.save()
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            raise Http404
