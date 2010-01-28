from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from piston.handler import BaseHandler
from piston.utils import rc, validate
from catalogue.models import Book
from catalogue.forms import BookImportForm


staff_required = user_passes_test(lambda user: user.is_staff)


class BookHandler(BaseHandler):
    model = Book
    fields = ('slug', 'title')
    
    @staff_required
    def read(self, request, slug=None):
        if slug:
            return get_object_or_404(Book, slug=slug)
        else:
            return Book.objects.all()
    
    @staff_required
    def create(self, request):
        form = BookImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.BAD_REQUEST

