# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import os.path
import shutil
import subprocess
from tempfile import mkdtemp
from StringIO import StringIO
from django.conf import settings
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def render_to_pdf(output_path, template, context=None, add_files=None):
    """Renders a TeXML document into a PDF file.

    :param str output_path: is where the PDF file should go
    :param str template: is a TeXML template path
    :param context: is context for rendering the template
    :param dict add_files: a dictionary of additional files XeTeX will need
    """

    import Texml.processor
    rendered = render_to_string(template, context)
    texml = StringIO(rendered.encode('utf-8'))
    tempdir = mkdtemp(prefix = "render_to_pdf-")
    tex_path = os.path.join(tempdir, "doc.tex")
    with open(tex_path, 'w') as tex_file:
        Texml.processor.process(texml, tex_file, encoding="utf-8")

    if add_files:
        for add_name, src_file in add_files.items():
            add_path = os.path.join(tempdir, add_name)
            if hasattr(src_file, "read"):
                with open(add_path, 'w') as add_file:
                    add_file.write(add_file.read())
            else:
                shutil.copy(src_file, add_path)

    cwd = os.getcwd()
    os.chdir(tempdir)
    try:
        subprocess.check_call(['xelatex', '-interaction=batchmode', tex_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            os.makedirs(os.path.dirname(output_path))
        except:
            pass
        shutil.move(os.path.join(tempdir, "doc.pdf"), output_path)
    finally:
        os.chdir(cwd)
        shutil.rmtree(tempdir)


def read_chunks(f, size=8192):
    chunk = f.read(size)
    while chunk:
        yield chunk
        chunk = f.read(size)


def generated_file_view(file_name, mime_type, send_name=None, signals=None):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    file_url = os.path.join(settings.MEDIA_URL, file_name)
    if send_name is None:
        send_name = os.path.basename(file_name)

    def signal_handler(*args, **kwargs):
        os.unlink(file_path)

    if signals:
        for signal in signals:
            signal.connect(signal_handler, weak=False)

    def decorator(func):
        def view(request, *args, **kwargs):
            if not os.path.exists(file_path) or True:
                func(file_path, *args, **kwargs)

            if hasattr(send_name, "__call__"):
                name = send_name()
            else:
                name = send_name

            response = HttpResponse(mimetype=mime_type)
            response['Content-Disposition'] = 'attachment; filename=%s' % name
            with open(file_path) as f:
                for chunk in read_chunks(f):
                    response.write(chunk)
            return response
        return view
    return decorator
