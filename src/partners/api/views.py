from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.generics import (ListAPIView, get_object_or_404)
from rest_framework import serializers
from api.fields import AbsoluteURLField
from catalogue.models import Book
from partners import models




class PartnerBookSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField(view_name='catalogue_api_book', view_args=['slug'])
    price = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['url', 'epub_url', 'price']

    def get_price(self, obj):
        if obj.pages is None:
            return None
        return self.context['partner'].get_price(obj.pages)


@method_decorator(never_cache, name='dispatch')
class PartnerBooksView(ListAPIView):
    serializer_class = PartnerBookSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['partner'] = get_object_or_404(models.Partner, key=self.kwargs['key'])
        return ctx

    def get_queryset(self):
        return Book.objects.filter(parent=None).filter(can_sell=True).exclude(pages=None)
